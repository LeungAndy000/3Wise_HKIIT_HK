"""One-time held-out evaluation of the selected, immutable message classifier."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from .metrics import binary_metrics, classification_metrics, quality_passed, review_metrics
from .training import read_rows, tokenize, evaluate_probabilities, save_json, file_hash, now, verify_data_files


def evaluate(model_dir, data_dir, output_dir):
    from .predictor import MessagePredictor
    model_dir, data_dir, output_dir = Path(model_dir), Path(data_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    mandatory = ('test', 'test_traditional_converted', 'external_mudou_binary', 'external_unreviewed')
    extra = tuple(name for name in ('fgrc_test', 'fgrc_traditional_converted', 'binary_domain_test')
                  if (data_dir / f'{name}.jsonl').is_file())
    verify_data_files(data_dir, mandatory + extra)
    predictor = MessagePredictor(model_dir, device_target='GPU', batch_size=128)
    identity = file_hash(model_dir / 'model.ckpt')
    report = {'status': 'running', 'model_id': predictor.model_id, 'checkpoint_sha256': identity,
              'selection': 'Checkpoint and thresholds selected on validation. For domain repair, original main, converted and external SMS tests were previously evaluated diagnostics; only the new domain tests were reserved before repair training.',
              'datasets': {}, 'started_at': now()}
    status_path = output_dir.parent / 'evaluation_status.json'
    started = time.perf_counter()
    padding_parity = None
    for name in mandatory + extra:
        path = data_dir / f'{name}.jsonl'
        if not path.exists():
            continue
        rows = read_rows(path)
        original_count = len(rows)
        exclusions = None
        binary_only = name in ('external_mudou_binary', 'binary_domain_test')
        unreviewed = name == 'external_unreviewed'
        if name == 'external_mudou_binary':
            exclusion_path = data_dir / 'external_near_duplicates.json'
            if not exclusion_path.exists():
                exclusion_path = Path(__file__).resolve().parents[1] / 'artifacts/data_audit/external_near_duplicates.json'
            if exclusion_path.exists():
                exclusions = json.loads(exclusion_path.read_text(encoding='utf-8'))
                if exclusions['source_jsonl_sha256'] != file_hash(path):
                    raise ValueError('External identity-exclusion audit belongs to different data')
                excluded = set(exclusions['excluded_record_ids'])
                rows = [row for row in rows if row['record_id'] not in excluded]
                order_hash = hashlib.sha256(('\n'.join(row['record_id'] for row in rows) + '\n').encode('utf-8')).hexdigest()
                if order_hash != exclusions['evaluated_record_order_sha256']:
                    raise ValueError('External evaluated row order differs from the text-only exclusion audit')
        encoded_rows = [{**row, 'label': row.get('label') if row.get('label') is not None else 0} for row in rows]
        encoded = tokenize(encoded_rows, predictor.tokenizer)
        def progress(done, total, elapsed):
            save_json(status_path, {'status': 'running', 'phase': 'evaluating', 'split': name,
                'rows_completed': done, 'total_rows': total, 'elapsed_seconds': time.perf_counter() - started,
                'eta_seconds': (total - done) * elapsed / max(done, 1), 'updated_at': now(),
                'results': report['datasets']})
        probabilities, timing = evaluate_probabilities(predictor.model, encoded, predictor._ms,
            progress=progress, batch_size=128, fixed_width=predictor.tokenizer.max_length)
        if name == 'test':
            sample_count = min(64, len(rows))
            sample = {key: values[:sample_count] for key, values in encoded.items()}
            bucket_scores, _ = evaluate_probabilities(predictor.model, sample, predictor._ms, batch_size=64)
            api_scores = np.asarray([list(value['scores'].values()) for value in
                                    predictor.predict([row['text'] for row in rows[:sample_count]])])
            padding_difference = float(np.max(np.abs(bucket_scores - probabilities[:sample_count])))
            runtime_difference = float(np.max(np.abs(api_scores - probabilities[:sample_count])))
            if padding_difference > .001 or runtime_difference > .001:
                raise ValueError('Length-bucket / fixed-padding / public predictor parity failed')
            padding_parity = {'passed': True, 'samples': sample_count,
                'maximum_probability_difference_buckets_vs_fixed': padding_difference,
                'maximum_probability_difference_public_predictor_vs_evaluation': runtime_difference}
        np.save(output_dir / f'{name}_probabilities.npy', probabilities)
        result = {'samples': len(rows), 'sha256': file_hash(path), 'timing': timing,
                  'sources': dict(Counter(row['source'] for row in rows)),
                  'scripts': dict(Counter(row['script_origin'] for row in rows)),
                  'predicted_label_counts': dict(Counter(('normal', 'spam', 'scam')[int(value)]
                                                       for value in probabilities.argmax(1)))}
        if exclusions is not None:
            result.update(original_samples=original_count, identity_exclusions=exclusions,
                          evaluated_record_order_sha256=order_hash)
        if unreviewed:
            result.update(evaluation_role='unlabelled_external_diagnostic', accuracy_measured=False,
                          reason='User reports/topic categories do not establish binary truth; no accuracy, F1 or recall computed')
        elif binary_only:
            labels = np.asarray([row['risk_label'] for row in rows], np.int32)
            result.update(evaluation_role='previously_seen_external_binary_diagnostic' if name == 'external_mudou_binary' else 'newly_reserved_binary_domain_test',
                label_semantics='normal versus unwanted; unwanted labels do not distinguish spam from scam',
                metrics=binary_metrics(labels, probabilities[:, 1:].sum(1) >= .5),
                metric_decision='sum_of_spam_and_scam_probabilities_at_least_0.5',
                review_decision_metrics=review_metrics(np.where(labels == 0, 0, -1), probabilities, predictor.thresholds),
                three_class_accuracy_measured=False)
        else:
            labels = encoded['labels']
            role = (('previously_evaluated_grouped_test' if extra else 'reserved_grouped_test') if name == 'test' else
                    'reserved_generated_message_test' if name == 'fgrc_test' else 'paired_script_conversion_robustness')
            result.update(evaluation_role=role,
                          metrics=classification_metrics(labels, probabilities),
                          review_decision_metrics=review_metrics(labels, probabilities, predictor.thresholds),
                          per_source={}, per_script={})
            if name.startswith('fgrc_'):
                result.update(text_provenance='case-derived generated SMS, not independently captured messages',
                              independent_real_sms_benchmark=False)
            for key, destination in (('source', 'per_source'), ('script_origin', 'per_script')):
                for value in sorted(set(row[key] for row in rows)):
                    selected = np.asarray([index for index, row in enumerate(rows) if row[key] == value])
                    result[destination][value] = classification_metrics(labels[selected], probabilities[selected])
            if name in ('test_traditional_converted', 'fgrc_traditional_converted'):
                paired_name = 'test' if name == 'test_traditional_converted' else 'fgrc_test'
                original = np.load(output_dir / f'{paired_name}_probabilities.npy')
                assert len(original) == len(probabilities)
                result['paired_original_decision_agreement'] = float(np.mean(original.argmax(1) == probabilities.argmax(1)))
                result['native_traditional_chinese_benchmark'] = False
                result['note'] = 'OpenCC script-converted original test messages, not newly collected Traditional Chinese ground truth'
        report['datasets'][name] = result
        save_json(output_dir / 'performance.json', report)
        print(json.dumps({'phase': 'evaluation_complete', 'split': name, 'metrics': result.get('metrics'),
                          'accuracy_measured': result.get('accuracy_measured', not unreviewed)}, ensure_ascii=False), flush=True)
    # Validate real public prediction API inputs on both orthographies, without
    # using hand-written demonstration cases as accuracy ground truth.
    examples = ['明天上午十點覆診，請帶同身份證。', '明天上午十点复诊，请带同身份证。',
                '您的账户异常，请立即提供验证码以免冻结。', '您的帳戶異常，請立即提供驗證碼以免凍結。']
    values = predictor.predict(examples)
    assert len(values) == 4 and all(np.isfinite(list(value['scores'].values())).all() for value in values)
    save_json(output_dir / 'example_predictions.json', {'examples': [{'message': text, **value}
              for text, value in zip(examples, values)], 'purpose': 'runtime demonstration; not accuracy ground truth'})
    assert file_hash(model_dir / 'model.ckpt') == identity
    main = report['datasets']['test']['metrics']
    traditional = report['datasets']['test_traditional_converted']['metrics']
    def binary_passed(metrics):
        return (metrics['f1'] >= .8 and metrics['recall'] >= .8
                and metrics['false_positive_rate'] is not None and metrics['false_positive_rate'] <= .1)
    extra_pass = {}
    for name in extra:
        metrics = report['datasets'][name]['metrics']
        extra_pass[name] = (binary_passed(metrics) and binary_passed(report['datasets'][name]['review_decision_metrics'])) if name == 'binary_domain_test' else bool(
            metrics['macro_f1_present_classes'] >= .8 and metrics['scam_recall'] >= .8
            and metrics['normal_false_positive_rate'] is not None and metrics['normal_false_positive_rate'] <= .1)
    report.update(status='completed', completed_at=now(), seconds=time.perf_counter() - started,
                  main_test_requirements_passed=quality_passed(main),
                  converted_traditional_requirements_passed=quality_passed(traditional),
                  external_binary_requirements_passed=binary_passed(report['datasets']['external_mudou_binary']['review_decision_metrics']),
                  supplementary_requirements_passed=all(extra_pass.values()),
                  supplementary_dataset_requirements=extra_pass,
                  production_ready=False,
                  native_traditional_chinese_validation='insufficient independent labelled real-world examples',
                  checkpoint_unchanged=True, padding_and_public_predictor_parity=padding_parity)
    save_json(output_dir / 'performance.json', report)
    save_json(model_dir / 'performance.json', report)
    save_json(status_path, {'status': 'completed', 'phase': 'evaluation_completed', 'updated_at': now(),
                           'metrics': main, 'traditional_metrics': traditional, 'results': report['datasets'],
                           'elapsed_seconds': time.perf_counter() - started, 'eta_seconds': 0})
    return report
