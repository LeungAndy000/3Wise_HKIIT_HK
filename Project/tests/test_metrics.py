import numpy as np
import pytest

from wisemessage.metrics import classification_metrics, review_metrics, select_thresholds


def test_metrics_keep_scam_misses_distinct_from_normal_false_alarms():
    labels = [0, 0, 1, 1, 2, 2]
    predictions = np.eye(3)[[0, 1, 1, 1, 2, 0]]
    result = classification_metrics(labels, predictions)
    assert result['accuracy'] == pytest.approx(4 / 6)
    assert result['scam_recall'] == .5
    assert result['normal_false_positive_rate'] == .5
    assert result['confusion_matrix'] == [[1, 1, 0], [0, 2, 0], [1, 0, 1]]


def test_source_metrics_do_not_count_absent_labels_as_failed_recall():
    result = classification_metrics([1, 2], np.eye(3)[[1, 2]])
    assert result['balanced_accuracy'] == 1.
    assert result['macro_f1_present_classes'] == 1.
    assert result['present_classes'] == ['spam', 'scam']
    assert result['normal_false_positive_rate'] is None


def test_review_thresholds_enforce_joint_false_alarm_cap():
    labels = np.asarray([0, 0, 0, 0, 1, 2])
    values = np.asarray([[.50, .45, .05], [.50, .05, .45], [.8, .1, .1], [.9, .05, .05],
                         [.1, .85, .05], [.1, .05, .85]])
    selected = select_thresholds(labels, values, max_normal_fpr=0.)
    result = review_metrics(labels, values, selected['thresholds'])
    assert result['false_positive_rate'] == 0.
    assert result['recall'] == 1.


def test_invalid_scores_cannot_produce_performance_claims():
    with pytest.raises(ValueError):
        classification_metrics([0], [[np.nan, .5, .5]])
    with pytest.raises(ValueError):
        classification_metrics([2], [[.8, .8, .8]])


def test_partial_label_unwanted_supervision_is_not_treated_as_normal():
    labels = np.array([0, -1, 1, 2])
    scores = np.array([[.9, .05, .05], [.4, .3, .3], [.1, .8, .1], [.1, .1, .8]])
    selection = select_thresholds(labels, scores, aggregate=True)
    result = review_metrics(labels, scores, selection['thresholds'])
    assert result['recall'] == 1.
    assert result['false_positive_rate'] == 0.
    assert result['confusion_matrix'] == {'tn': 1, 'fp': 0, 'fn': 0, 'tp': 3}
