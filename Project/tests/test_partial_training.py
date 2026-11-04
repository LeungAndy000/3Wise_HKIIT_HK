"""Unknown spam/scam labels must supervise risk without inventing a subtype."""

import numpy as np
import pytest

from wisemessage.training import (partial_label_loss, training_class_weights,
    validate_training_rows, validation_metrics, validation_quality_passed,
    validation_selection_key, audit_review_calibration)


def test_partial_rows_require_binary_positive_provenance():
    rows = [{'label': label} for label in (0, 1, 2)]
    validate_training_rows(rows + [{'label': -1, 'risk_label': 1,
                                   'supervision': 'binary_unwanted'}], 'train')
    for invalid in ({'label': -1}, {'label': -1, 'risk_label': 0, 'supervision': 'binary_unwanted'},
                    {'label': 0, 'risk_label': 1}, {'label': 3}):
        with pytest.raises(ValueError):
            validate_training_rows(rows + [invalid], 'train')


def test_unknown_subtype_does_not_inflate_known_class_counts():
    counts, weights, partial_weight = training_class_weights([0, 0, 1, 2, -1, -1, -1])
    assert counts.tolist() == [2, 1, 1]
    assert weights.mean() == pytest.approx(1.)
    assert min(weights[1:]) <= partial_weight <= max(weights[1:])


def test_mixed_partial_loss_matches_probability_definition_and_weight_normalization():
    import mindspore as ms
    probabilities = np.asarray([[.7, .2, .1], [.1, .6, .3], [.1, .2, .7], [.4, .25, .35]], np.float32)
    labels = ms.Tensor([0, 1, 2, -1], ms.int32)
    weights = np.asarray([.5, 1., 2.], np.float32)
    sample_weights = np.asarray([.5, 1., 2., 1.5])
    expected = np.average(-np.log([.7, .6, .7, .6]), weights=sample_weights)
    actual = partial_label_loss(ms.Tensor(np.log(probabilities)), labels, weights, partial_weight=1.5)
    assert float(actual.asnumpy()) == pytest.approx(expected, abs=3e-6)
    # Duplicating the batch or scaling every weight cannot change the objective.
    repeated = partial_label_loss(ms.Tensor(np.tile(np.log(probabilities), (2, 1))),
                                 ms.Tensor([0, 1, 2, -1] * 2, ms.int32), weights * 9, partial_weight=13.5)
    assert float(repeated.asnumpy()) == pytest.approx(expected, abs=3e-6)


def test_partial_loss_has_finite_gradients_for_extreme_wrong_logits_and_no_subtype_preference():
    import mindspore as ms
    labels = ms.Tensor([-1, -1], ms.int32)
    logits = ms.Tensor(np.asarray([[1000., -1000., -999.], [-1000., 1000., 1000.]], np.float32))
    function = lambda values: partial_label_loss(values, labels, [1., 1., 1.])
    loss, gradients = ms.value_and_grad(function)(logits)
    assert np.isfinite(loss.asnumpy()).all()
    assert np.isfinite(gradients.asnumpy()).all()
    assert gradients.asnumpy()[0, 0] > 0
    assert np.all(gradients.asnumpy()[0, 1:] < 0)
    # Exchanging spam and scam scores leaves partial supervision unchanged.
    swapped = function(ms.Tensor(logits.asnumpy()[:, [0, 2, 1]]))
    assert float(swapped.asnumpy()) == pytest.approx(float(loss.asnumpy()), rel=1e-7)


def test_validation_separates_unknown_subtypes_and_uses_aggregate_risk():
    labels = [0, 1, 2, -1, -1]
    probabilities = [[.9, .05, .05], [.05, .9, .05], [.05, .05, .9],
                     [.4, .3, .3], [.95, .025, .025]]
    metrics = validation_metrics(labels, probabilities)
    assert metrics['samples'] == metrics['fully_labelled_samples'] == 3
    assert metrics['validation_samples_total'] == 5
    assert metrics['partial_label_samples'] == 2
    assert metrics['macro_f1'] == 1.
    assert metrics['binary_unwanted']['recall'] == .75
    assert metrics['partial_binary']['recall'] == .5
    assert metrics['partial_unwanted_recall'] == .5
    assert not validation_quality_passed(metrics)
    improved = validation_metrics(labels, probabilities[:4] + [[.4, .3, .3]])
    assert validation_quality_passed(improved)
    assert validation_selection_key(improved) > validation_selection_key(metrics)


def test_partial_gate_cannot_be_hidden_by_many_correct_known_scam_examples():
    labels = [0] * 20 + [1] * 20 + [2] * 100 + [-1] * 10
    probabilities = [[.9, .05, .05]] * 20 + [[.05, .9, .05]] * 20 + [[.05, .05, .9]] * 100 + [[.9, .05, .05]] * 10
    metrics = validation_metrics(labels, probabilities)
    assert metrics['binary_unwanted']['recall'] > .9
    assert metrics['macro_f1'] == 1.
    assert metrics['partial_binary']['recall'] == 0.
    assert not validation_quality_passed(metrics)


def test_calibration_cannot_hide_unknown_subtype_misses_behind_many_known_examples():
    labels = [0] * 20 + [1] * 20 + [2] * 100 + [-1] * 2
    probabilities = np.asarray([[.9, .05, .05]] * 20 + [[.05, .9, .05]] * 20 +
                               [[.05, .05, .9]] * 100 + [[.4, .3, .3]] * 2)
    metrics = validation_metrics(labels, probabilities)
    proposed = {'thresholds': {'spam': 1., 'scam': 1., 'unwanted': .8},
                'selection': 'aggregate_f1_optimum'}
    selected = audit_review_calibration(labels, probabilities, proposed, metrics)
    assert selected['proposed_review_audit']['binary_unwanted']['f1'] > .99
    assert selected['proposed_review_audit']['partial_binary']['recall'] == 0.
    assert selected['thresholds']['unwanted'] == .5
    assert selected['selected_review_audit']['partial_binary']['recall'] == 1.
    assert selected['quality_requirements_passed']
    assert selected['proposed_calibration'] == proposed


def test_failed_review_quality_is_recorded_when_no_joint_validation_fallback_passes():
    labels = [0, 1, 2, -1]
    probabilities = np.asarray([[.9, .05, .05], [.05, .9, .05], [.05, .05, .9], [.9, .05, .05]])
    metrics = validation_metrics(labels, probabilities)
    proposed = {'thresholds': {'spam': 1., 'scam': 1., 'unwanted': .8}}
    result = audit_review_calibration(labels, probabilities, proposed, metrics)
    assert not result['quality_requirements_passed']
    assert not result['review_quality_requirements_passed']
    assert 'fallback_reason' not in result


def test_warm_start_loads_the_trained_head_and_preserves_original_source_identity(tmp_path):
    import mindspore as ms
    from wisemessage.config import MessageConfig
    from wisemessage.model import MessageClassifier
    from wisemessage.training import initialize_classifier, file_hash, save_json
    config = MessageConfig(vocab_size=8, hidden_size=8, num_hidden_layers=1,
                           num_attention_heads=2, intermediate_size=16, max_position_embeddings=8)
    bundle = tmp_path / 'model'
    bundle.mkdir()
    config.save(bundle / 'config.json')
    (bundle / 'vocab.txt').write_text('[PAD]\n[UNK]\n[CLS]\n[SEP]\n[MASK]\n你\n好\n嗎\n', encoding='utf-8')
    source = {'checkpoint_sha256': 'a' * 64, 'tokenizer_sha256': file_hash(bundle / 'vocab.txt')}
    trained = MessageClassifier(config)
    trained.classifier.bias.set_data(ms.Tensor([1., 2., 3.], ms.float32))
    ms.save_checkpoint(trained, str(bundle / 'model.ckpt'))
    manifest = {'format_version': 1, 'framework': 'mindspore', 'task': 'sms_spam_scam_detection',
        'checkpoint_type': 'message_classifier', 'model_id': 'unit-test-trained',
        'id2label': {'0': 'normal', '1': 'spam', '2': 'scam'}, 'checkpoint': 'model.ckpt',
        'config': 'config.json', 'vocab': 'vocab.txt', 'max_length': 8,
        'checkpoint_sha256': file_hash(bundle / 'model.ckpt'),
        'config_sha256': file_hash(bundle / 'config.json'), 'tokenizer_sha256': source['tokenizer_sha256'],
        'config_fingerprint': config.fingerprint(), 'pretrained': source}
    save_json(bundle / 'manifest.json', manifest)
    target = MessageClassifier(config)
    audit = initialize_classifier(target, tmp_path / 'unused', source, config, ms, bundle)
    assert np.array_equal(target.classifier.bias.asnumpy(), [1., 2., 3.])
    assert audit['all_encoder_and_classifier_parameters_loaded']
    assert audit['optimizer_state_reinitialized']
    wrong_source = {**source, 'checkpoint_sha256': 'b' * 64}
    with pytest.raises(ValueError, match='different original pretrained'):
        initialize_classifier(target, tmp_path / 'unused', wrong_source, config, ms, bundle)
