import numpy as np
from sklearn import metrics
from sklearn.utils.multiclass import unique_labels


def macro_averaged_mean_absolute_error(y_true, y_pred):
    labels = unique_labels(y_true, y_pred)
    mae = []
    for possible_class in labels:
        indices = np.flatnonzero(y_true == possible_class)

        mae.append(metrics.mean_absolute_error(y_true[indices], y_pred[indices],))

    return np.sum(mae) / len(mae)


def calculate_metrics(y_true, y_pred):
    if np.in1d(y_pred, y_true, invert=True).sum() > 0:
        raise ValueError("There are non-existent labels in predictions")

    weights = np.array([1.0, 1.0, 1.5, 1.5, 1.5])
    recall_multi = metrics.recall_score(y_true, y_pred, average=None)
    weighted_accuracy = np.sum(np.multiply(recall_multi, weights)) / np.sum(weights)
    mamae = macro_averaged_mean_absolute_error(y_true, y_pred)
    return weighted_accuracy - 0.25 * mamae
