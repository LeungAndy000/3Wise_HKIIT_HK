"""Native MindSpore fine-tuning of pretrained MiniRBT for Chinese SMS messages.

All encoder layers and the classifier are trainable. Validation alone selects
checkpoints and thresholds. Test data is loaded only by a later evaluation stage.
Checkpoints are versioned and retained; this module never deletes files.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import time

import numpy as np

from .metrics import binary_metrics, classification_metrics, quality_passed, select_thresholds, review_metrics


def now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # One writer owns each status path. Readers tolerate an incomplete refresh.
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def read_rows(path):
    rows = [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if not rows or not all(isinstance(row.get('text'), str) and row['text'].strip() for row in rows):
        raise ValueError(f'No usable message texts in {path}')
    return rows


def verify_data_files(data_dir, names):
    data_dir = Path(data_dir)
    manifest = json.loads((data_dir / 'manifest.json').read_text(encoding='utf-8'))
    for name in names:
        entry = manifest['files'][name]
        if Path(entry['filename']).name != entry['filename']:
            raise ValueError('Prepared dataset filenames must remain inside the data directory')
        if file_hash(data_dir / entry['filename']) != entry['sha256']:
            raise ValueError(f'Prepared dataset SHA256 mismatch: {name}')
    return manifest


def tokenize(rows, tokenizer):
    parts = []
    for start in range(0, len(rows), 2048):
        parts.append(tokenizer.encode_batch([row['text'] for row in rows[start:start + 2048]]))
    result = {key: np.concatenate([part[key] for part in parts]) for key in parts[0]}
    result['lengths'] = result['attention_mask'].sum(1).astype(np.int32)
    result['labels'] = np.asarray([row['label'] for row in rows], dtype=np.int32)
    return result


def validate_training_rows(rows, split):
    """Accept unknown subtypes only when their binary supervision is explicit."""
    labels = np.asarray([row.get('label') for row in rows])
    if not np.isin(labels, [-1, 0, 1, 2]).all():
        raise ValueError(f'{split} contains an unsupported message label')
    if set(labels[labels >= 0]) != {0, 1, 2}:
        raise ValueError(f'{split} must contain all three fully labelled classes')
    for row in rows:
        if row['label'] == -1:
            if row.get('risk_label') != 1 or row.get('supervision') != 'binary_unwanted':
                raise ValueError('Unknown spam/scam subtype requires explicit binary_unwanted supervision')
        elif row.get('risk_label', int(row['label'] != 0)) != int(row['label'] != 0):
            raise ValueError('Binary risk label contradicts its known three-class label')


def training_class_weights(labels):
    """Compute class weights without treating unknown subtypes as a class.

    Partial examples receive the prevalence-weighted mean weight of the known
    unwanted classes. The loss normalizes by the actual sum of sample weights.
    """
    labels = np.asarray(labels, dtype=np.int32)
    if not np.isin(labels, [-1, 0, 1, 2]).all():
        raise ValueError('Unsupported training label')
    known = labels[labels >= 0]
    counts = np.bincount(known, minlength=3)
    if np.any(counts == 0):
        raise ValueError('Each known class needs training examples')
    weights = np.sqrt(len(known) / (3 * counts))
    weights /= weights.mean()
    weights = weights.astype(np.float32)
    partial_weight = float(np.float32(np.average(weights[1:], weights=counts[1:])))
    return counts, weights, partial_weight


def partial_label_loss(logits, labels, class_weights, partial_weight=1.):
    """Weighted exact-label CE or -log(P(spam)+P(scam)) for unknown subtype.

    Work entirely in log space: even extreme, confidently wrong logits yield
    finite losses and gradients. No synthetic spam/scam target is assigned.
    """
    import mindspore as ms
    from mindspore import ops
    if len(logits.shape) != 2 or logits.shape[1] != 3 or labels.shape != (logits.shape[0],):
        raise ValueError('Expected [N,3] logits and [N] labels')
    if not isinstance(class_weights, ms.Tensor):
        class_weights = ms.Tensor(np.asarray(class_weights, np.float32))
    if class_weights.shape != (3,):
        raise ValueError('Expected three class weights')
    known = labels >= 0
    safe_labels = ops.maximum(labels, ops.zeros_like(labels))
    log_probabilities = ops.log_softmax(logits, axis=-1)
    targets = ops.one_hot(safe_labels, 3, ms.Tensor(1., ms.float32), ms.Tensor(0., ms.float32))
    exact_losses = -ops.sum(targets * log_probabilities, 1)
    partial_losses = -ops.logsumexp(log_probabilities[:, 1:], dim=-1)
    losses = ops.where(known, exact_losses, partial_losses)
    sample_weights = ops.where(known, ops.gather(class_weights, safe_labels, 0),
                               ms.Tensor(float(partial_weight), ms.float32))
    return ops.sum(losses * sample_weights) / ops.sum(sample_weights)


def validation_metrics(labels, probabilities):
    """Keep three-class truth separate from the binary-only unwanted examples."""
    labels = np.asarray(labels, dtype=np.int32)
    probabilities = np.asarray(probabilities)
    if not np.isin(labels, [-1, 0, 1, 2]).all() or probabilities.shape != (len(labels), 3):
        raise ValueError('Invalid partial-label validation arrays')
    known = labels >= 0
    if not known.any():
        raise ValueError('Three-class validation requires fully labelled examples')
    metrics = classification_metrics(labels[known], probabilities[known])
    # classification_metrics also validates normalization on every row, even
    # those whose three-class subtype is unknown, without inventing its truth.
    if not np.isfinite(probabilities).all() or (probabilities < 0).any() or not np.allclose(probabilities.sum(1), 1, atol=1e-5):
        raise ValueError('Expected finite normalized validation probabilities')
    predicted_unwanted = probabilities[:, 1:].sum(1) >= .5
    metrics.update(validation_samples_total=len(labels), fully_labelled_samples=int(known.sum()),
                   partial_label_samples=int((~known).sum()),
                   binary_unwanted=binary_metrics((labels != 0).astype(np.int32), predicted_unwanted),
                   three_class_label_semantics='normal/spam/scam on fully labelled rows only',
                   binary_decision='P(spam)+P(scam)>=0.5')
    if (~known).any():
        selected = (labels == 0) | ~known
        metrics['partial_binary'] = binary_metrics((labels[selected] != 0).astype(np.int32),
                                                    predicted_unwanted[selected])
        metrics['partial_unwanted_recall'] = float(predicted_unwanted[~known].mean())
        metrics['partial_binary_label_semantics'] = 'known normal versus unwanted with unknown spam/scam subtype'
    metrics['quality_requirements_passed'] = validation_quality_passed(metrics)
    return metrics


def validation_quality_passed(metrics):
    if not quality_passed(metrics):
        return False
    if metrics.get('partial_label_samples', 0):
        for key in ('binary_unwanted', 'partial_binary'):
            binary = metrics[key]
            if (binary['f1'] < .8 or binary['recall'] < .8 or
                    binary['false_positive_rate'] is None or binary['false_positive_rate'] > .1):
                return False
    return True


def audit_review_calibration(labels, probabilities, calibration, metrics):
    """Check the deployed review rule on both known and subtype-unknown truth.

    Maximizing aggregate F1 can hide poor recall on a small partial-label group.
    A validated fixed-0.5 rule is retained when that otherwise occurs.
    """
    labels, probabilities = np.asarray(labels), np.asarray(probabilities)
    has_partial = bool(np.any(labels == -1))
    def passes(binary):
        return (binary['f1'] >= .8 and binary['recall'] >= .8 and
                binary['false_positive_rate'] is not None and binary['false_positive_rate'] <= .1)
    def audit(thresholds):
        result = {'thresholds': dict(thresholds),
                  'binary_unwanted': review_metrics(labels, probabilities, thresholds)}
        result['quality_requirements_passed'] = passes(result['binary_unwanted'])
        if has_partial:
            selected = (labels == 0) | (labels == -1)
            result['partial_binary'] = review_metrics(labels[selected], probabilities[selected], thresholds)
            result['quality_requirements_passed'] &= passes(result['partial_binary'])
        return result
    result = dict(calibration)
    proposed = audit(result['thresholds'])
    result['proposed_review_audit'] = proposed
    if has_partial and not proposed['quality_requirements_passed'] and validation_quality_passed(metrics):
        fixed = {'spam': 1., 'scam': 1., 'unwanted': .5}
        fallback = audit(fixed)
        if fallback['quality_requirements_passed']:
            result['proposed_calibration'] = dict(calibration)
            result.update(thresholds=fixed, review_metrics=fallback['binary_unwanted'],
                          selection='validation_only_joint_quality_fallback_to_validated_aggregate_0.5',
                          fallback_reason='Aggregate F1 optimum fails binary or unknown-subtype validation requirements')
    selected = audit(result['thresholds'])
    result['selected_review_audit'] = selected
    result['review_quality_requirements_passed'] = selected['quality_requirements_passed']
    result['quality_requirements_passed'] = bool(validation_quality_passed(metrics) and selected['quality_requirements_passed'])
    return result


def validation_selection_key(metrics):
    """Rank the weakest required detection score before aggregate accuracy."""
    scores = [metrics['macro_f1'], metrics['scam_recall']]
    fprs = [metrics['normal_false_positive_rate']]
    if metrics.get('partial_label_samples', 0):
        for name in ('binary_unwanted', 'partial_binary'):
            scores.extend((metrics[name]['f1'], metrics[name]['recall']))
            fprs.append(metrics[name]['false_positive_rate'])
    return (validation_quality_passed(metrics), min(scores), metrics['macro_f1'],
            metrics['scam_recall'], -max(value if value is not None else 1. for value in fprs))


def initialize_classifier(model, pretrained, source_manifest, config, ms, init_model_dir=None):
    """Load the exact complete warm start or the original encoder, never mix them."""
    pretrained = Path(pretrained)
    if init_model_dir is not None:
        from .predictor import read_classifier_manifest
        initial_manifest, files = read_classifier_manifest(init_model_dir)
        initial_config = config.__class__.from_json(files['config'])
        if (initial_config.fingerprint() != config.fingerprint() or
                initial_manifest['config_fingerprint'] != config.fingerprint() or
                file_hash(files['vocab']) != source_manifest['tokenizer_sha256']):
            raise ValueError('Warm-start classifier architecture or vocabulary differs from the pretrained MiniRBT')
        initial_pretrained = initial_manifest.get('pretrained', {})
        if initial_pretrained.get('checkpoint_sha256') != source_manifest['checkpoint_sha256']:
            raise ValueError('Warm-start classifier uses a different original pretrained encoder')
        missing, unexpected = ms.load_param_into_net(model, ms.load_checkpoint(str(files['checkpoint'])), strict_load=True)
        if missing or unexpected:
            raise ValueError(f'Incomplete warm-start classifier load: {missing} {unexpected}')
        return {'model_dir': str(Path(init_model_dir).resolve()),
                'model_id': initial_manifest['model_id'],
                'checkpoint_sha256': initial_manifest['checkpoint_sha256'],
                'all_encoder_and_classifier_parameters_loaded': True,
                'optimizer_state_reinitialized': True}
    missing, unexpected = ms.load_param_into_net(model, ms.load_checkpoint(str(pretrained / 'model.ckpt')), strict_load=True)
    if set(missing) != {'classifier.weight', 'classifier.bias'} or unexpected:
        raise ValueError(f'Unexpected pretrained load: {missing} {unexpected}')
    return None


def batches(split, seed=None, batch_size=128):
    lengths = split['lengths']
    buckets = [32, 64, 96, 128, 160, 192, 224, split['input_ids'].shape[1]]
    buckets = sorted(set(min(value, split['input_ids'].shape[1]) for value in buckets))
    groups = np.searchsorted(buckets, lengths, side='left')
    rng = np.random.default_rng(seed)
    result = []
    for index, width in enumerate(buckets):
        selected = np.flatnonzero(groups == index)
        if seed is not None:
            rng.shuffle(selected)
        size = min(batch_size * 2, 256) if width <= 64 else (min(batch_size, 64) if width >= 192 else batch_size)
        for start in range(0, len(selected), size):
            result.append((width, selected[start:start + size]))
    if seed is not None:
        rng.shuffle(result)
    return result


def evaluate_probabilities(model, split, ms, progress=None, batch_size=128, fixed_width=None):
    model.set_train(False)
    count = len(split['labels'])
    scores = np.empty((count, 3), np.float32)
    started = time.perf_counter()
    work = batches(split, batch_size=batch_size) if fixed_width is None else [
        (fixed_width, np.arange(start, min(start + batch_size, count))) for start in range(0, count, batch_size)]
    completed = 0
    for index, (width, selected) in enumerate(work):
        tensors = [ms.Tensor(np.ascontiguousarray(split[key][selected, :width]), ms.int32)
                   for key in ('input_ids', 'attention_mask', 'token_type_ids')]
        logits = model(*tensors).asnumpy()
        if not np.isfinite(logits).all():
            raise ValueError('Nonfinite evaluation logits')
        values = np.exp(logits - logits.max(1, keepdims=True))
        scores[selected] = values / values.sum(1, keepdims=True)
        completed += len(selected)
        if progress and (index == 0 or index % 10 == 0 or completed == count):
            progress(completed, count, time.perf_counter() - started)
    return scores, {'samples': count, 'seconds': time.perf_counter() - started,
                    'tokenization_included': False, 'padding_policy': 'length_buckets' if fixed_width is None else f'fixed_{fixed_width}'}


def train(pretrained, data_dir, run_dir, epochs=6, max_length=256, budget_minutes=35,
          batch_size=128, learning_rate=5e-5, seed=2026, init_model_dir=None):
    from .runtime import configure_runtime
    ms = configure_runtime('GPU', seed=seed)
    from mindspore import nn, ops
    from .config import MessageConfig
    from .model import MessageClassifier
    from .tokenizer import MessageTokenizer
    pretrained, data_dir, run_dir = Path(pretrained), Path(data_dir), Path(run_dir)
    checkpoints = run_dir / 'checkpoints'
    checkpoints.mkdir(parents=True, exist_ok=True)
    if any(checkpoints.iterdir()):
        raise ValueError('Use a fresh run; existing checkpoints are retained')
    status_path = run_dir / 'training_status.json'
    started, end = time.perf_counter(), time.time() + budget_minutes * 60
    record = {'status': 'running', 'phase': 'tokenizing', 'framework': 'mindspore',
              'pretrained_model': 'hfl/minirbt-h256', 'training_started': True,
              'started_at': now(), 'epochs': epochs, 'max_length': max_length}
    def update(**values):
        record.update(values)
        record.update(updated_at=now(), elapsed_seconds=time.perf_counter() - started)
        save_json(status_path, record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
    update()
    source_manifest = json.loads((pretrained / 'manifest.json').read_text(encoding='utf-8'))
    if file_hash(pretrained / 'model.ckpt') != source_manifest['checkpoint_sha256']:
        raise ValueError('Pretrained checkpoint identity mismatch')
    config = MessageConfig.from_json(pretrained / 'config.json')
    if (config.fingerprint() != source_manifest['config_fingerprint'] or
            file_hash(pretrained / 'vocab.txt') != source_manifest['tokenizer_sha256']):
        raise ValueError('Pretrained configuration or vocabulary identity mismatch')
    verify_data_files(data_dir, ('train', 'validation'))
    tokenizer = MessageTokenizer(pretrained / 'vocab.txt', max_length=max_length)
    splits = {}
    for name in ('train', 'validation'):
        rows = read_rows(data_dir / f'{name}.jsonl')
        validate_training_rows(rows, name)
        splits[name] = tokenize(rows, tokenizer)
        update(split=name, rows_completed=len(rows), total_rows=len(rows))
    counts, weights, partial_weight = training_class_weights(splits['train']['labels'])
    weight_tensor = ms.Tensor(weights)
    model = MessageClassifier(config)
    initialization = initialize_classifier(model, pretrained, source_manifest, config, ms, init_model_dir)
    trainable = list(model.trainable_params())
    encoder_count = sum(int(parameter.size) for parameter in model.bert.get_parameters())
    classifier_count = sum(int(parameter.size) for parameter in model.classifier.get_parameters())
    total_count = sum(int(parameter.size) for parameter in trainable)
    assert total_count == encoder_count + classifier_count
    first_batches = batches(splits['train'], seed, batch_size)
    total_steps = len(first_batches) * epochs
    warmup = max(10, int(total_steps * .1))
    rates = []
    for step in range(total_steps):
        scale = (step + 1) / warmup if step < warmup else .1 + .9 * .5 * (1 + math.cos(math.pi * (step - warmup) / max(total_steps - warmup, 1)))
        rates.append(learning_rate * scale)
    decay = [parameter for parameter in trainable if not any(key in parameter.name for key in ('bias', 'beta', 'gamma'))]
    no_decay = [parameter for parameter in trainable if any(key in parameter.name for key in ('bias', 'beta', 'gamma'))]
    optimizer = nn.AdamWeightDecay([{'params': decay, 'weight_decay': .01},
                                   {'params': no_decay, 'weight_decay': 0.}],
                                  learning_rate=ms.Tensor(np.asarray(rates, np.float32)))
    def forward(ids, mask, types, labels):
        logits = model(ids, mask, types)
        return partial_label_loss(logits, labels, weight_tensor, partial_weight)
    gradient = ms.value_and_grad(forward, None, optimizer.parameters)
    steps, examples_seen, best = 0, 0, None
    history = []
    update(phase='training', split='train', trainable_parameters=total_count,
           encoder_parameters=encoder_count, classifier_parameters=classifier_count,
           class_counts=counts.tolist(), class_weights=weights.tolist(), total_steps=total_steps,
           partial_label_training_samples=int((splits['train']['labels'] == -1).sum()),
           partial_label_sample_weight=partial_weight, initialization=initialization,
           loss_semantics='weighted exact-label CE; unknown unwanted subtype uses -log(P(spam)+P(scam)); normalized by sample-weight sum')
    for epoch in range(1, epochs + 1):
        losses = []
        model.set_train(True)
        work = batches(splits['train'], seed + epoch, batch_size)
        for width, selected in work:
            if time.time() >= end and steps:
                break
            tensors = [ms.Tensor(np.ascontiguousarray(splits['train'][key][selected, :width]), ms.int32)
                       for key in ('input_ids', 'attention_mask', 'token_type_ids')]
            labels = ms.Tensor(splits['train']['labels'][selected], ms.int32)
            loss, gradients = gradient(*tensors, labels)
            finite = bool(ops.isfinite(loss).asnumpy())
            finite_gradients = bool(ops.stack([ops.all(ops.isfinite(value)) for value in gradients]).all().asnumpy())
            if not finite or not finite_gradients:
                raise FloatingPointError('Nonfinite training loss or gradient; checkpoint not updated')
            optimizer(ops.clip_by_global_norm(gradients, 1.))
            losses.append(float(loss.asnumpy()))
            steps += 1
            examples_seen += len(selected)
            if steps == 1 or steps % 20 == 0:
                elapsed = time.perf_counter() - started
                update(phase='training', split='train', epoch=epoch, global_step=steps,
                       rows_completed=examples_seen, total_rows=len(splits['train']['labels']) * epochs,
                       examples_seen=examples_seen, loss=float(np.mean(losses[-20:])),
                       batch_size=len(selected), sequence_width=width,
                       rows_per_second=examples_seen / elapsed,
                       eta_seconds=(total_steps - steps) * elapsed / steps)
        def progress(done, total, elapsed):
            update(phase='validating', split='validation', epoch=epoch,
                   rows_completed=done, total_rows=total, eta_seconds=(total - done) * elapsed / max(done, 1))
        probabilities, timing = evaluate_probabilities(model, splits['validation'], ms, progress)
        metrics = validation_metrics(splits['validation']['labels'], probabilities)
        path = checkpoints / f'epoch_{epoch:02d}_step_{steps:05d}'
        path.mkdir(parents=True, exist_ok=False)
        ms.save_checkpoint(model, str(path / 'model.ckpt'))
        ms.save_checkpoint(optimizer, str(path / 'optimizer.ckpt'))
        np.save(path / 'validation_probabilities.npy', probabilities)
        save_json(path / 'validation.json', {'metrics': metrics, 'timing': timing, 'epoch': epoch, 'global_step': steps})
        key = validation_selection_key(metrics)
        entry = {'epoch': epoch, 'global_step': steps, 'examples_seen': examples_seen,
                 'training_loss': float(np.mean(losses)) if losses else None,
                 'validation': metrics, 'checkpoint': str(path / 'model.ckpt')}
        history.append(entry)
        save_json(run_dir / 'training_history.json', history)
        if best is None or key > best[0]:
            best = (key, path, metrics, probabilities.copy(), epoch, steps)
        update(phase='validation_complete', epoch=epoch, validation_metrics=metrics,
               best_validation=best[2], best_quality_passed=validation_quality_passed(best[2]))
        if time.time() >= end:
            break
        # A full warm-start fine-tune gets at least three epochs. Later epochs
        # stop when two completed epochs fail to improve the selected model.
        if epoch >= 3 and epoch - best[4] >= 2:
            break
    if best is None:
        raise RuntimeError('No validated classifier checkpoint was produced')
    # Passing explicit binary truth also remains correct with legacy threshold
    # helpers whose labels>0 predicate would otherwise misread label=-1.
    has_partial = bool(np.any(splits['train']['labels'] == -1) or np.any(splits['validation']['labels'] == -1))
    calibration = select_thresholds((splits['validation']['labels'] != 0).astype(np.int32), best[3],
                                    aggregate=has_partial)
    calibration['partial_label_samples'] = int((splits['validation']['labels'] == -1).sum())
    calibration['binary_label_semantics'] = 'normal versus unwanted, including unknown unwanted subtypes'
    calibration = audit_review_calibration(splits['validation']['labels'], best[3], calibration, best[2])
    validation_passed = bool(validation_quality_passed(best[2]) and calibration['quality_requirements_passed'])
    best[2]['calibrated_review_quality_requirements_passed'] = calibration['review_quality_requirements_passed']
    best[2]['quality_requirements_passed'] = validation_passed
    output = run_dir / 'model'
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Existing model bundle preserved; choose a new run')
    shutil.copyfile(best[1] / 'model.ckpt', output / 'model.ckpt')
    config.save(output / 'config.json')
    shutil.copyfile(pretrained / 'vocab.txt', output / 'vocab.txt')
    manifest = {'format_version': 1, 'framework': 'mindspore', 'framework_version': ms.__version__,
        'task': 'sms_spam_scam_detection', 'checkpoint_type': 'message_classifier',
        'model_id': f'wisemessage-minirbt-h256-step{best[5]}',
        'checkpoint': 'model.ckpt', 'config': 'config.json', 'vocab': 'vocab.txt',
        'checkpoint_sha256': file_hash(output / 'model.ckpt'), 'config_sha256': file_hash(output / 'config.json'),
        'tokenizer_sha256': file_hash(output / 'vocab.txt'), 'config_fingerprint': config.fingerprint(),
        'id2label': {str(index): label for index, label in enumerate(('normal', 'spam', 'scam'))},
        'max_length': max_length, 'do_lower_case': True, 'thresholds': calibration['thresholds'],
        'threshold_selection': calibration, 'validation_metrics': best[2],
        'provisional_quality_requirements': {'macro_f1': .8, 'scam_recall': .8, 'max_normal_false_positive_rate': .1,
            'binary_unwanted_f1_when_partial_labels_present': .8,
            'binary_unwanted_recall_when_partial_labels_present': .8,
            'partial_binary_f1_when_partial_labels_present': .8,
            'partial_binary_recall_when_partial_labels_present': .8},
        'validation_requirements_passed': validation_passed,
        'pretrained': source_manifest, 'trainable_parameters': total_count,
        'training': {'all_encoder_layers_trainable': True, 'classifier_trainable': True,
                     'selected_epoch': best[4], 'completed_epochs': len(history), 'global_step': best[5],
                     'learning_rate': learning_rate, 'max_epochs': epochs, 'seed': seed,
                     'class_weights': weights.tolist(), 'training_rows': len(splits['train']['labels']),
                     'partial_label_training_samples': int((splits['train']['labels'] == -1).sum()),
                     'partial_label_sample_weight': partial_weight,
                     'loss': 'normalized weighted exact-label cross_entropy plus partial-label negative_log_unwanted_probability',
                     'initialization': initialization,
                     'train_sha256': file_hash(data_dir / 'train.jsonl'),
                     'validation_sha256': file_hash(data_dir / 'validation.jsonl'),
                     'test_used_for_selection': False},
        'languages': ['Traditional Chinese', 'Simplified Chinese'],
        'decision_note': 'Class scores are model estimates, not verified sender identity or calibrated safety guarantees',
        'usage': 'Research prototype; dataset source terms and external evaluation limitations apply',
        'created_at': now()}
    save_json(output / 'manifest.json', manifest)
    summary = {'model_dir': str(output), 'validation': best[2], 'calibration': calibration,
               'validation_requirements_passed': validation_passed,
               'parameters': total_count, 'checkpoint_bytes': (output / 'model.ckpt').stat().st_size,
               'epochs_completed': len(history), 'selected_epoch': best[4], 'global_steps_completed': steps,
               'training_seconds': time.perf_counter() - started, 'training_started': True}
    save_json(run_dir / 'training_result.json', summary)
    update(status='completed', phase='training_completed', metrics=best[2], model_dir=str(output),
           global_step=steps, rows_completed=examples_seen,
           result=summary, eta_seconds=0)
    return summary
