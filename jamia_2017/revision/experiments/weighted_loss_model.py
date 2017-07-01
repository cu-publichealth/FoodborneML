import numpy as np
from chainer import Variable, Chain, reporter, functions as F
from weighted_softmax_cross_entropy import weighted_softmax_cross_entropy
from baseline_experiment_util import importance_weighted_pr_curve, area_under_pr_curve

class WeightedLossModel(Chain):
    def __init__(self, predictor):
        super(WeightedLossModel, self).__init__()
        with self.init_scope():
            self.predictor = predictor

    def __call__(self, xs, ys, weights, is_biased):
        y_scores = self.predictor(xs)
        y_pred_probs = F.softmax(y_scores)
        ys = self._maybe_change_type(ys)
        loss = weighted_softmax_cross_entropy(y_scores, ys, instance_weight=weights)
        reporter.report({'loss':loss}, self)

        # get the area under pr curve
        # print ys[:5], y_pred_probs.data[:5,1]
        precisions, recalls, thresholds = importance_weighted_pr_curve(
            ys, y_pred_probs.data[:,1], is_biased)
        aupr = area_under_pr_curve(precisions, recalls)
        half_threshold = (np.abs(thresholds-.5)).argmin()
        reporter.report({
            'precisions':precisions,
            'recalls':recalls,
            'thresholds':thresholds,
            'aupr':aupr,
            'precision@t={0:0.2f}'.format(thresholds[half_threshold]):precisions[half_threshold],
            'recall@t={0:0.2f}'.format(thresholds[half_threshold]):recalls[half_threshold]
        }, self)
        return loss

    def _maybe_change_type(self, X, new_type=np.int32):
        if type(X) is Variable:
            X.data = X.data.astype(new_type)
        else:
            X = X.astype(new_type)
        return X
