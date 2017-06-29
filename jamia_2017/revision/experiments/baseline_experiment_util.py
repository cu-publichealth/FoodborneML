import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import StratifiedKFold
from sklearn.externals import joblib

def setup_baseline_data(train_regime='gold', test_regime='gold', random_seed=0, silver_size=10000):
    test_split_date = datetime.strptime('1/1/2017', '%d/%m/%Y')
    biased = pd.read_csv('../data/biased.csv', encoding='utf8')
    biased.date = pd.to_datetime(biased.date)
    old_biased = biased[biased['date'] < test_split_date]
    new_biased = biased[biased['date'] >= test_split_date]

    unbiased = pd.read_csv('../data/unbiased.csv', encoding='utf8')
    unbiased.date = pd.to_datetime(unbiased.date)
    U = len(unbiased) + len(biased)

    if train_regime == 'gold':
        old_unbiased = pd.read_excel('../data/historical_unbiased.xlsx', encoding='utf8')
        old_unbiased.date = pd.to_datetime(old_unbiased.date)
    elif train_regime == 'silver':
        old_unbiased = unbiased[unbiased.date < test_split_date]
        old_unbiased = old_unbiased.sample(silver_size, random_state=random_seed)
        # assume the biased complement are negative examples
        old_unbiased['is_foodborne'] = 'No'
        old_unbiased['is_multiple'] = 'No'
    else:
        raise ValueError, "Regime must be 'silver' or 'gold'"

    if test_regime == 'gold':
        # print '[WARNING] THE TEST DATA IS NOT CORRECT FOR THIS REGIME YET'
        # old_unbiased = pd.read_excel('../data/historical_unbiased.xlsx', encoding='utf8')
        new_unbiased = pd.read_excel('../data/current_nonbiased.xlsx', encoding='utf8')
        new_unbiased.rename(columns={'Is_Foodborne':'is_foodborne',
                              'Is_Multiple_Foodborne':'is_multiple',
                              'created':'date'},
                            inplace=True)
        new_unbiased.is_multiple = new_unbiased.is_multiple.map({'Maybe':'No','No':'No'})
        new_unbiased.date = pd.to_datetime(new_unbiased.date)

    elif test_regime == 'silver':
        unbiased = pd.read_csv('../data/unbiased.csv', encoding='utf8')
        unbiased.date = pd.to_datetime(unbiased.date)
        new_unbiased = unbiased[unbiased.date >= test_split_date]
        new_unbiased = new_unbiased.sample(silver_size, random_state=random_seed)
        # assume the biased complement are negative examples
        new_unbiased['is_foodborne'] = 'No'
        new_unbiased['is_multiple'] = 'No'
    else:
        raise ValueError, "Regime must be 'silver' or 'gold'"

    old_biased['is_foodborne'] = old_biased['is_foodborne'].map({'Yes':1, 'No':0})
    old_unbiased['is_foodborne'] = old_unbiased['is_foodborne'].map({'Yes':1, 'No':0})
    new_biased['is_foodborne'] = new_biased['is_foodborne'].map({'Yes':1, 'No':0})
    new_unbiased['is_foodborne'] = new_unbiased['is_foodborne'].map({'Yes':1, 'No':0})

    old_biased['is_multiple'] = old_biased['is_multiple'].map({'Yes':1, 'No':0})
    old_unbiased['is_multiple'] = old_unbiased['is_multiple'].map({'Yes':1, 'No':0})
    new_biased['is_multiple'] = new_biased['is_multiple'].map({'Yes':1, 'No':0})
    new_unbiased['is_multiple'] = new_unbiased['is_multiple'].map({'Yes':1, 'No':0})

    return {
        'train_data': {
            'text':old_biased['text'].tolist() + old_unbiased['text'].tolist(),
            'is_foodborne':old_biased['is_foodborne'].tolist() + old_unbiased['is_foodborne'].tolist(),
            'is_multiple':old_biased['is_multiple'].tolist() + old_unbiased['is_multiple'].tolist(),
            'is_biased':[True]*len(old_biased) + [False]*len(old_unbiased)
        },
        'test_data': {
            'text':new_biased['text'].tolist() + new_unbiased['text'].tolist(),
            'is_foodborne':new_biased['is_foodborne'].tolist() + new_unbiased['is_foodborne'].tolist(),
            'is_multiple':new_biased['is_multiple'].tolist() + new_unbiased['is_multiple'].tolist(),
            'is_biased':[True]*len(new_biased) + [False]*len(new_unbiased)
        },
        'U':U
    }

def calc_train_importance_weights(is_biased, U):
    B = float(sum(is_biased))
    Bc = len(is_biased) - B
#     print 'U:{}, B:{}, Bc:{}'.format(U,B, Bc)
    w_B = 1./U
    w_Bc = (1.-(B/U))*(1./Bc)
    iw = np.array([w_B if label else w_Bc for label in is_biased])
    rescaled = (len(is_biased)/iw.sum())*iw
#     print 'w_B:{}, w_Bc:{}'.format(*sorted(np.unique(rescaled).tolist()))
    return rescaled

def importance_weighted_precision_recall(y_trues, y_pred_probs, is_biased, threshold=.5):
    # find the precision at this threshold
    in_Up = y_pred_probs >= threshold # same as predictions at this threshold
    Up = in_Up.sum().astype(np.float32) + 1e-15 # for stability when there are no positive predictions
    biased_and_Up = is_biased & in_Up
    unbiased_and_Up = (~is_biased) & in_Up
    bias_rate = sum(biased_and_Up)/Up
    bias_term = bias_rate * (1./Up) * ((y_trues == 1) & biased_and_Up).sum()
    unbias_term = (1. - bias_rate) * (1./Up) * ((y_trues == 1) & unbiased_and_Up).sum()
    precision = bias_term + unbias_term

    # find recall at this threshold
    in_Ur = y_trues == 1 # same as true positives
    Ur = in_Ur.sum().astype(np.float32) + 1e-15 # for stability when there are no positive examples
    biased_and_Ur = is_biased & in_Ur
    unbiased_and_Ur = (~is_biased) & in_Ur
    bias_rate = sum(biased_and_Ur)/Ur
    bias_term = bias_rate * (1./Ur) * (in_Up & biased_and_Ur).sum() # in_Up is same as preds
    unbias_term = (1. - bias_rate) * (1./Ur) * (in_Up & unbiased_and_Ur).sum()
    recall = bias_term + unbias_term

    return precision, recall

def importance_weighted_pr_curve(y_trues, y_pred_probs, is_biased):
    thresholds = np.linspace(1, 0, 100)
    precisions, recalls = [], []
    for t in thresholds:
        p, r = importance_weighted_precision_recall(y_trues, y_pred_probs, is_biased, t)
        precisions.append(p)
        recalls.append(r)
        if r >= 1.:
            break
    return np.array(precisions), np.array(recalls), thresholds[:len(precisions)]

def area_under_pr_curve(precisions, recalls):
    # calculate area under curve using trapezoidal integration
    aupr = 0.
    for i in range(len(precisions)-1):
        aupr += .5 * (recalls[i+1] - recalls[i]) * (precisions[i] + precisions[i+1])
    return aupr

def score_model(model, xs, ys, bs, U, fit_weight_kwd, n_cv_splits, random_seed):
    folds = StratifiedKFold(n_splits=n_cv_splits, random_state=random_seed)
    stratify_on_these = ['{},{}'.format(y,b) for y,b in zip(ys, bs)]
    dev_scores = []
    for train_idx, dev_idx in folds.split(np.zeros(len(xs)), stratify_on_these):

        train_text = np.array(xs)[train_idx]
        train_ys = np.array(ys)[train_idx]
        train_is_biased = np.array(bs)[train_idx]

        dev_text = np.array(xs)[dev_idx]
        dev_ys = np.array(ys)[dev_idx]
        dev_is_biased = np.array(bs)[dev_idx]

        train_importance_weights = calc_train_importance_weights(train_is_biased, U)
        model.fit(train_text, train_ys, **{fit_weight_kwd:train_importance_weights})
        scored_devs = model.predict_proba(dev_text)[:,1]
        dev_precisions, dev_recalls, _ = importance_weighted_pr_curve(dev_ys, scored_devs, dev_is_biased)
        dev_aupr = area_under_pr_curve(dev_precisions, dev_recalls)
#         print 'AUPR: {0:2.2f}'.format(dev_aupr)
        dev_scores.append(dev_aupr)
    return np.array(dev_scores)

def random_search(model, random_hyperparams, model_fname, **score_kwds):
    experiments = []
    N = len(random_hyperparams.values()[0])
    best_score = -1.0
    best_params = {}
    for i in range(N):
        random_hyperparam = {k:v[i] for k,v in random_hyperparams.items()}
        model.set_params(**random_hyperparam)
        print '\n------- Experiment {}/{} -------'.format(i+1, N)
        print 'params: {}'.format(random_hyperparam)
        experiment = {'i':i,
                      'params':model.get_params(),
                      'scores':score_model(model, **score_kwds)}
        experiments.append(experiment)
        print 'scores: {}'.format(experiments[-1]['scores'])
        score = experiments[-1]['scores'].mean()
        if score > best_score:
            print 'New best: {0:2.2f}'.format(score)
            best_score = score
            joblib.dump(model, model_fname)
    return experiments
