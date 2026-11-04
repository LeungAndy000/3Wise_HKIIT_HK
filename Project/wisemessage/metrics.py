"""Explicit three-class and review-decision metrics for labelled SMS messages."""
import numpy as np

LABELS = ('normal', 'spam', 'scam')


def classification_metrics(labels, probabilities):
    labels = np.asarray(labels, dtype=np.int32)
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if labels.ndim != 1 or probabilities.shape != (len(labels), 3) or not len(labels):
        raise ValueError('Expected nonempty labels and [N,3] probabilities')
    if not np.isin(labels, [0, 1, 2]).all() or not np.isfinite(probabilities).all():
        raise ValueError('Invalid labels or nonfinite predictions')
    if (probabilities < 0).any() or not np.allclose(probabilities.sum(1), 1, atol=1e-5):
        raise ValueError('Expected normalized probabilities')
    predictions = probabilities.argmax(1)
    matrix = np.zeros((3, 3), dtype=np.int64)
    np.add.at(matrix, (labels, predictions), 1)
    classes = {}
    for index, name in enumerate(LABELS):
        tp = int(matrix[index, index])
        support = int(matrix[index].sum())
        predicted = int(matrix[:, index].sum())
        precision = tp / predicted if predicted else 0.
        recall = tp / support if support else 0.
        classes[name] = {'support': support, 'precision': precision, 'recall': recall,
                         'f1': 2 * precision * recall / (precision + recall) if precision + recall else 0.}
    normal_count = int(matrix[0].sum())
    return {'samples': len(labels), 'accuracy': float(np.trace(matrix) / len(labels)),
            'macro_f1': float(np.mean([value['f1'] for value in classes.values()])),
            'macro_f1_present_classes': float(np.mean([value['f1'] for value in classes.values() if value['support']])),
            'present_classes': [name for name, value in classes.items() if value['support']],
            'balanced_accuracy': float(np.mean([value['recall'] for value in classes.values() if value['support']])),
            'scam_recall': classes['scam']['recall'],
            'normal_false_positive_rate': float((matrix[0, 1] + matrix[0, 2]) / normal_count) if normal_count else None,
            'per_class': classes, 'confusion_matrix': matrix.tolist(),
            'confusion_matrix_order': list(LABELS)}


def binary_metrics(labels, predictions):
    labels, predictions = np.asarray(labels), np.asarray(predictions, dtype=bool)
    if labels.shape != predictions.shape or not len(labels) or not np.isin(labels, [0, 1]).all():
        raise ValueError('Expected equally sized nonempty binary arrays')
    tp = int(np.sum((labels == 1) & predictions))
    tn = int(np.sum((labels == 0) & ~predictions))
    fp = int(np.sum((labels == 0) & predictions))
    fn = int(np.sum((labels == 1) & ~predictions))
    precision, recall = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    return {'samples': len(labels), 'accuracy': (tp + tn) / len(labels),
            'precision': precision, 'recall': recall,
            'f1': 2 * tp / max(2 * tp + fp + fn, 1),
            'false_positive_rate': fp / (fp + tn) if fp + tn else None,
            'confusion_matrix': {'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp}}


def review_metrics(labels, probabilities, thresholds):
    labels, probabilities = np.asarray(labels), np.asarray(probabilities)
    if 'unwanted' in thresholds:
        flagged = probabilities[:, 1:].sum(1) >= thresholds['unwanted']
    else:
        flagged = ((probabilities[:, 1] >= thresholds['spam']) |
                   (probabilities[:, 2] >= thresholds['scam']))
    # -1 denotes source-labelled unwanted SMS with an unknown spam/scam subtype.
    if not np.isin(labels, [-1, 0, 1, 2]).all():
        raise ValueError('Invalid message supervision labels')
    return binary_metrics((labels != 0).astype(np.int32), flagged)


def select_thresholds(labels, probabilities, max_normal_fpr=.10, aggregate=False):
    """Select review thresholds on validation only, with a joint false-alarm cap."""
    candidates = np.unique(np.r_[np.linspace(.20, .90, 29), .95, .99, 1.])
    labels, probabilities = np.asarray(labels), np.asarray(probabilities)
    best = None
    if aggregate:
        for threshold in candidates:
            thresholds = {'spam': 1., 'scam': 1., 'unwanted': float(threshold)}
            metrics = review_metrics(labels, probabilities, thresholds)
            if metrics['false_positive_rate'] is not None and metrics['false_positive_rate'] <= max_normal_fpr:
                key = (metrics['f1'], metrics['recall'], -metrics['false_positive_rate'], -abs(threshold - .5))
                if best is None or key > best[0]:
                    best = key, thresholds, metrics
        if best is None:
            raise ValueError('No aggregate validation threshold satisfies the false-positive cap')
        return {'thresholds': best[1], 'review_metrics': best[2],
                'selection': 'validation_only_maximum_unwanted_f1_using_sum_of_spam_and_scam_probabilities',
                'max_normal_false_positive_rate': max_normal_fpr}
    for spam in candidates:
        for scam in candidates:
            thresholds = {'spam': float(spam), 'scam': float(scam)}
            metrics = review_metrics(labels, probabilities, thresholds)
            if metrics['false_positive_rate'] is not None and metrics['false_positive_rate'] <= max_normal_fpr:
                key = (metrics['f1'], metrics['recall'], -metrics['false_positive_rate'], -abs(spam - .5) - abs(scam - .5))
                if best is None or key > best[0]:
                    best = key, thresholds, metrics
    if best is None:
        raise ValueError('No validation review thresholds satisfy the false-positive cap')
    return {'thresholds': best[1], 'review_metrics': best[2],
            'selection': 'validation_only_maximum_unwanted_f1_with_normal_false_positive_cap',
            'max_normal_false_positive_rate': max_normal_fpr}


def quality_passed(metrics):
    return (metrics['macro_f1'] >= .8 and metrics['scam_recall'] >= .8
            and metrics['normal_false_positive_rate'] is not None
            and metrics['normal_false_positive_rate'] <= .10)
