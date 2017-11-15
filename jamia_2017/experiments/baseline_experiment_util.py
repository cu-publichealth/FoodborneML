""" All helper functions for training and evaluating models. """
import numpy as np
import numpy.random as npr
import pandas as pd
from datetime import datetime
import os.path as osp
import itertools
from pprint import pprint

import matplotlib.pyplot as plt
import seaborn as sb
sb.set()

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib

def setup_baseline_data(train_regime='gold',
                        test_regime='gold',
                        data_path='../data',
                        random_seed=0,
                        silver_size=10000,
                        test_split_date='1/1/2017'):
    """ Read in the cleaned data, split it up and format for evaluation. """
    test_split_date = datetime.strptime(test_split_date, '%m/%d/%Y')
    biased = pd.read_csv(osp.join(data_path, 'fixed_biased.csv'), encoding='utf8')
    biased.date = pd.to_datetime(biased.date)
    old_biased = biased[biased['date'] < test_split_date]
    new_biased = biased[biased['date'] >= test_split_date]

    unbiased = pd.read_csv(osp.join(data_path, 'fixed_unbiased.csv'), encoding='utf8')
    unbiased.date = pd.to_datetime(unbiased.date)
    U = len(unbiased) + len(biased)

    if train_regime == 'gold':
        old_unbiased = pd.read_excel(osp.join(data_path, 'historical_unbiased.xlsx'),
                                     encoding='utf8')
        old_unbiased.date = pd.to_datetime(old_unbiased.date)
    elif train_regime == 'silver':
        old_unbiased = unbiased[unbiased.date < test_split_date]
        old_unbiased = old_unbiased.sample(silver_size, random_state=random_seed)
        # assume the biased complement are negative examples
        old_unbiased.loc[:,'is_foodborne'] = 'No'
        old_unbiased.loc[:,'is_multiple'] = 'No'
    elif train_regime == 'biased':
        old_unbiased = pd.DataFrame(columns=old_biased.columns)
    else:
        raise ValueError, "Regime must be 'silver', 'gold', or 'biased'"

    if test_regime == 'gold':
        new_unbiased = pd.read_excel(osp.join(data_path, 'fixed_current_nonbiased.xlsx'),
                                     encoding='utf8')
        new_unbiased.date = pd.to_datetime(new_unbiased.date)

    elif test_regime == 'silver':
        unbiased = pd.read_csv(osp.join(data_path, 'fixed_unbiased.csv'), encoding='utf8')
        unbiased.date = pd.to_datetime(unbiased.date)
        new_unbiased = unbiased[unbiased.date >= test_split_date]
        new_unbiased = new_unbiased.sample(silver_size, random_state=random_seed)
        # assume the biased complement are negative examples
        new_unbiased.loc[:,'is_foodborne'] = 'No'
        new_unbiased.loc[:,'is_multiple'] = 'No'
    elif test_regime == 'biased':
        new_unbiased = pd.DataFrame(columns=new_biased.columns)
    else:
        raise ValueError, "Regime must be 'silver' or 'gold'"

    old_biased.loc[:,'is_foodborne'] = old_biased['is_foodborne'].map({'Yes':1, 'No':0})
    old_unbiased.loc[:,'is_foodborne'] = old_unbiased['is_foodborne'].map({'Yes':1, 'No':0})
    new_biased.loc[:,'is_foodborne'] = new_biased['is_foodborne'].map({'Yes':1, 'No':0})
    new_unbiased.loc[:,'is_foodborne'] = new_unbiased['is_foodborne'].map({'Yes':1, 'No':0})

    old_biased.loc[:,'is_multiple'] = old_biased['is_multiple'].map({'Yes':1, 'No':0})
    old_unbiased.loc[:,'is_multiple'] = old_unbiased['is_multiple'].map({'Yes':1, 'No':0})
    new_biased.loc[:,'is_multiple'] = new_biased['is_multiple'].map({'Yes':1, 'No':0})
    new_unbiased.loc[:,'is_multiple'] = new_unbiased['is_multiple'].map({'Yes':1, 'No':0})

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
    """ Get the IW for bias-corrected error rate. """
    B = float(sum(is_biased))
    Bc = len(is_biased) - B + 1e-15 # for stability when all are biased
    w_B = 1./U
    w_Bc = (1.-(B/U))*(1./Bc)
    iw = np.array([w_B if label else w_Bc for label in is_biased])
    rescaled = (len(is_biased)/iw.sum())*iw
    return rescaled

def importance_weighted_precision_recall(y_trues, y_pred_probs, is_biased, threshold=.5):
    """ Calculate the precision and recall with bias correction. """
    # find the precision at this threshold
    in_Up = y_pred_probs >= threshold # same as predictions at this threshold
    Up = in_Up.sum().astype(np.float32) # number of positive predictions
    
    if Up > 0.: # model has made some positive classifications
        biased_and_Up = is_biased & in_Up
        unbiased_and_Up = (~is_biased) & in_Up
        p_bias_rate = sum(biased_and_Up)/Up
        p_bias_term = p_bias_rate * (1./Up) * ((y_trues == 1) & biased_and_Up).sum()
        p_unbias_term = (1. - p_bias_rate) * (1./Up) * ((y_trues == 1) & unbiased_and_Up).sum()
        precision = p_bias_term + p_unbias_term
    else: # model has no positive classifications, which means it's made no precision errors
        precision = 1.

    # find recall at this threshold
    in_Ur = y_trues == 1 # same as true positives
    Ur = in_Ur.sum().astype(np.float32) # number of positive examples
    if Ur > 0.: # there are positive examples
        biased_and_Ur = is_biased & in_Ur
        unbiased_and_Ur = (~is_biased) & in_Ur
        r_bias_rate = sum(biased_and_Ur)/Ur
        r_bias_term = r_bias_rate * (1./Ur) * (in_Up & biased_and_Ur).sum() # in_Up is same as preds
        r_unbias_term = (1. - r_bias_rate) * (1./Ur) * (in_Up & unbiased_and_Ur).sum()
        recall = r_bias_term + r_unbias_term
    else: # there are no examples to recall, which means there are no positives to falsely labe negative
        recall = 1.
    #if precision == 0. and recall == 0.:
    #    print '{t} ; {prate:0.2f}, {Up} : {rrate:0.2f}, {Ur}:: '.format(t=threshold, prate=p_bias_rate, rrate=r_bias_rate, Up=Up, Ur=Ur)
    return precision, recall

def importance_weighted_pr_curve(y_trues, y_pred_probs, is_biased, n_thresholds=100):
    """ Calculate a whole bias-corrected PR-curve. """
    thresholds = np.linspace(1, 0, n_thresholds)
    precisions, recalls = [], []
    for t in thresholds:
        p, r = importance_weighted_precision_recall(y_trues, y_pred_probs, is_biased, t)
        precisions.append(p)
        recalls.append(r)
        if r >= 1.:
            break
    return np.array(precisions), np.array(recalls), thresholds[:len(precisions)]

def area_under_pr_curve(precisions, recalls):
    """ Calculate area under curve using trapezoidal integration. """
    aupr = 0.
    for i in range(len(precisions)-1):
        aupr += .5 * (recalls[i+1] - recalls[i]) * (precisions[i] + precisions[i+1])
    return aupr

def score_model(model, xs, ys, bs, U, fit_weight_kwd, n_cv_splits, random_seed):
    """ For dev tuning, take a model and score using cross-validation. """
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
        dev_scores.append(dev_aupr)
    return np.array(dev_scores)

def random_search(model, random_hyperparams, model_fname, **score_kwds):
    """ Perform a random search experiment for some model on a random grid and write to a file. """
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

def f1(precision, recall):
    return 2.*precision*recall/(precision+recall+1e-15)

def ci(xbar, samples, confidence_level=.95):
    """ Calculate an empirical confidence interval. """
    diffs = [ xbar - xi for xi in samples]
    alpha = (1. - confidence_level)/2.
    ci_bottom = xbar - np.percentile(diffs, 100.*(1-alpha))
    ci_top = xbar - np.percentile(diffs, 100.*alpha)
    return ci_bottom, ci_top

def iw_bootstrap_score_ci(trues, preds, is_biased, scoring_func,
                          B=1000, confidence_level=.95,
                          random_seed=None,
                          **scoring_func_kwds):
    """ Compute a bootstrapped estimate of the importance weighted model score and stratified resampling.

    An intuitive and practical guide to bootstrap estimation:
    https://ocw.mit.edu/courses/mathematics/18-05-introduction-to-probability-and-statistics-spring-2014/readings/MIT18_05S14_Reading24.pdf
    """
    if random_seed: npr.seed(random_seed)
    xbar = scoring_func(trues, preds, is_biased, **scoring_func_kwds)
    samples = []
    biased_idxs = np.argwhere(is_biased).ravel()
    nonbiased_idxs = np.argwhere(~is_biased).ravel()
    print
    for i in range(B):
        print '\rB: {}/{}'.format(i,B),
        if len(nonbiased_idxs):
            sample = np.hstack([npr.choice(biased_idxs, len(biased_idxs)),
                                npr.choice(nonbiased_idxs, len(nonbiased_idxs))])
        else:
            sample = npr.choice(biased_idxs, len(biased_idxs))
        samples.append(scoring_func(trues[sample], preds[sample], is_biased[sample], **scoring_func_kwds))
    ci_bottom, ci_top = ci(xbar, samples, confidence_level)
    return xbar, ci_bottom, ci_top, samples

def bootstrap_f1_ci(trues, preds, is_biased, random_seed=None, **bootstrap_kwds):
    """ Get bootstrap confidence intervals around IW-F1 score. """
    def scorer(trues, preds, is_biased):
        p, r = importance_weighted_precision_recall(trues, preds, is_biased, threshold=.5)
        return f1(p,r)
    return iw_bootstrap_score_ci(trues, preds, is_biased, scorer,
                              random_seed=random_seed,
                              **bootstrap_kwds)

def bootstrap_aupr_ci(trues, preds, is_biased, random_seed=None, **bootstrap_kwds):
    """ Get bootstrap confidence intervals around IW-AUPR score. """
    def scorer(trues, preds, is_biased):
        #plt.hist(preds, bins=100, alpha=.25)
        ps, rs, ts = importance_weighted_pr_curve(trues, preds, is_biased, n_thresholds=50)
        #plt.plot(rs, ps, alpha=.5)
        return area_under_pr_curve(ps, rs)
    return iw_bootstrap_score_ci(trues, preds, is_biased, scorer,
                              random_seed=random_seed,
                              **bootstrap_kwds)

def subplot_confusion_matrix(cm, classes,
                             fig, ax,
                             precision=None, recall=None, f1_ci=None,
                             normalize=False,
                             title='Confusion matrix',
                             cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.

    Modified from http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py
    """
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.set_title(title)
    fig.colorbar(im, ax=ax)
    tick_marks = np.arange(len(classes))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(classes)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    ax.set_ylabel('True label')
    xlabel = 'Predicted label'
    if (precision is not None) and (recall is not None):
        xlabel += '\nPrecision: {0:2.3f}, Recall: {1:2.3f}'.format(precision, recall)
    if f1_ci is not None:
        xlabel +='\nF1: {0:2.3f}, CI:({1:2.3f}, {2:2.3f})'.format(*f1_ci)
    ax.set_xlabel(xlabel)
    ax.grid(False)

def model_report(model, title, label_key, save_fname=None, test_data=None, **bootstrap_kwds):
    """ Generate the test report of a model, for use in the paper. """
    y_trues = np.array(test_data[label_key])
    is_biased = np.array(test_data['is_biased'])
    y_preds = model.predict(test_data['text'])
    y_pred_probs = model.predict_proba(test_data['text'])[:,1]
    ps, rs, ts = importance_weighted_pr_curve(y_trues, y_pred_probs, is_biased)
    aupr, aupr_ci_bottom, aupr_ci_top, samples = bootstrap_aupr_ci(y_trues, y_pred_probs, is_biased, **bootstrap_kwds)
#     print '--- {} ---'.format(title)
#     print '  Precision@.5, Recall@.5: {0:2.2f}, {1:2.2f}'.format(precision, recall)
#     print '  AUPR: {0:2.2f}'.format(aupr)
    fig, axs = plt.subplots(2,2, figsize=(8,8))
    axs[0,0].plot(rs, ps, label='AUPR: {0:2.3f} CI=({1:2.3f}, {2:2.3f})'.format(aupr, aupr_ci_bottom, aupr_ci_top))
    axs[0,0].set_title('Precision Recall Curve')
    axs[0,0].set_xlabel('Recall')
    axs[0,0].set_ylabel('Precision')
    axs[0,0].legend(loc=8)

    # plot out cms for mixed, biased, and nonbiased
    precision_m, recall_m = importance_weighted_precision_recall(y_trues, y_pred_probs, is_biased, .5)
    f1_ci_m = bootstrap_f1_ci(y_trues, y_pred_probs, is_biased, **bootstrap_kwds)
    cm = confusion_matrix(y_trues, y_preds)
    subplot_confusion_matrix(cm,
                             ['Not Sick', 'Sick'],
                             fig,
                             axs[0,1],
                             title='Mixed Bias',
                             precision=precision_m,
                             recall=recall_m,
                             f1_ci=f1_ci_m[:3])
    # biased
    precision_b, recall_b = importance_weighted_precision_recall(y_trues[is_biased],
                                                                 y_pred_probs[is_biased],
                                                                is_biased[is_biased], .5)
    f1_ci_b = bootstrap_f1_ci(y_trues[is_biased],
                              y_pred_probs[is_biased],
                              is_biased[is_biased],
                              **bootstrap_kwds)
    cm = confusion_matrix(y_trues[is_biased], y_preds[is_biased])
    subplot_confusion_matrix(cm,
                             ['Not Sick', 'Sick'],
                             fig,
                             axs[1,0],
                             title='Biased',
                             precision=precision_b,
                             recall=recall_b,
                             f1_ci=f1_ci_b[:3])
    # nonbiased
    # there is no point to reporting precision, recall here since there are no positives
    # but we do it anyways in case the dataset were to change
    precision, recall = importance_weighted_precision_recall(y_trues[~is_biased],
                                                             y_pred_probs[~is_biased],
                                                             is_biased[~is_biased], .5)
    cm = confusion_matrix(y_trues[~is_biased], y_preds[~is_biased])
    subplot_confusion_matrix(cm, ['Not Sick', 'Sick'], fig, axs[1,1],
                             title="Nonbiased (all No's)",
                             precision=precision, recall=recall)

    fig.suptitle(title + ' Test Report', fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.92)
    if save_fname:
        plt.savefig(save_fname+'_report.pdf')

    # also plot the bootstrap historgrams to make sure they look ok
    fig2, axs2 = plt.subplots(1,3, figsize=(12,4))
    axs2[0].hist(samples, bins=100)
    axs2[0].axvline(aupr, color='red')
    axs2[0].axvspan(aupr_ci_bottom, aupr_ci_top, alpha=.25, color='red')
    axs2[0].set_title('AUPR Bootstrap')
    axs2[1].hist(f1_ci_m[3], bins=100)
    axs2[1].axvline(f1_ci_m[0], color='red')
    axs2[1].axvspan(f1_ci_m[1], f1_ci_m[2], alpha=.25, color='red')
    axs2[1].set_title('Mixed Bias F1 Boostrap')
    axs2[2].hist(f1_ci_b[3], bins=100)
    axs2[2].axvline(f1_ci_b[0], color='red')
    axs2[2].axvspan(f1_ci_b[1], f1_ci_b[2], alpha=.25, color='red')
    axs2[2].set_title('Biased F1 Boostrap')
    fig2.suptitle(title + ' Bootstrap Histograms', fontsize=14)
    fig2.tight_layout()
    fig2.subplots_adjust(top=0.85)
    if save_fname:
        plt.savefig(save_fname+'_bootstrap_hists.pdf')

    return {
        'aupr':aupr,
        'aupr_ci':(aupr_ci_bottom, aupr_ci_top),
        'aupr_samples':samples,
        'mixed_precision':precision_m,
        'mixed_recall':recall_m,
        'mixed_f1':f1_ci_m[0],
        'mixed_f1_ci':f1_ci_m[1:3],
        'mixed_f1_samples':f1_ci_m[3],
        'biased_precision':precision_b,
        'biased_recall':recall_b,
        'biased_f1':f1_ci_b[0],
        'biased_f1_ci':f1_ci_b[1:3],
        'biased_f1_samples':f1_ci_b[3]
    }

def prototype_model_report(trues, preds, is_biased, title, save_fname=None, **bootstrap_kwds):
    """ Doesn't run model, since prototype scores are loaded from csv. (It's a java model)."""
    y_trues = np.array(trues)
    is_biased = np.array(is_biased)
    y_pred_probs = np.array(preds)
    y_preds = (y_pred_probs >= .5).astype(np.int32)
    ps, rs, ts = importance_weighted_pr_curve(y_trues, y_pred_probs, is_biased)
    aupr, aupr_ci_bottom, aupr_ci_top, samples = bootstrap_aupr_ci(y_trues, y_pred_probs, is_biased, **bootstrap_kwds)
    fig, axs = plt.subplots(2,2, figsize=(8,8))
    axs[0,0].plot(rs, ps, label='AUPR: {0:2.3f} CI=({1:2.3f}, {2:2.3f})'.format(aupr, aupr_ci_bottom, aupr_ci_top))
    axs[0,0].set_title('Precision Recall Curve')
    axs[0,0].set_xlabel('Recall')
    axs[0,0].set_ylabel('Precision')
    axs[0,0].legend(loc=8)

    # plot out cms for mixed, biased, and nonbiased
    precision_m, recall_m = importance_weighted_precision_recall(y_trues, y_pred_probs, is_biased, .5)
    f1_ci_m = bootstrap_f1_ci(y_trues, y_pred_probs, is_biased, **bootstrap_kwds)
    cm = confusion_matrix(y_trues, y_preds)
    subplot_confusion_matrix(cm, ['Not Sick', 'Sick'], fig, axs[0,1],
                             title='Mixed Bias',
                             precision=precision_m, recall=recall_m, f1_ci=f1_ci_m[:3])
    # biased
    precision_b, recall_b = importance_weighted_precision_recall(y_trues[is_biased],
                                                             y_pred_probs[is_biased],
                                                             is_biased[is_biased], .5)
    f1_ci_b = bootstrap_f1_ci(y_trues[is_biased], y_pred_probs[is_biased], is_biased[is_biased], **bootstrap_kwds)
    cm = confusion_matrix(y_trues[is_biased], y_preds[is_biased])
    subplot_confusion_matrix(cm, ['Not Sick', 'Sick'], fig, axs[1,0],
                             title='Biased',
                             precision=precision_b, recall=recall_b, f1_ci=f1_ci_b[:3])
    # nonbiased
    # there is no point to reporting precision, recall here since there are no positives
    # but we do it anyways in case the dataset were to change
    precision, recall = importance_weighted_precision_recall(y_trues[~is_biased],
                                                             y_pred_probs[~is_biased],
                                                             is_biased[~is_biased], .5)
    cm = confusion_matrix(y_trues[~is_biased], y_preds[~is_biased])
    subplot_confusion_matrix(cm, ['Not Sick', 'Sick'], fig, axs[1,1],
                             title="Nonbiased (all No's)",
                             precision=precision, recall=recall)



    fig.suptitle(title + ' Test Report', fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.92)
    if save_fname:
        plt.savefig(save_fname+'_report.pdf')

    # also plot the bootstrap historgrams to make sure they look ok
    fig2, axs2 = plt.subplots(1,3, figsize=(12,4))
    axs2[0].hist(samples, bins=100)
    axs2[0].axvline(aupr, color='red')
    axs2[0].axvspan(aupr_ci_bottom, aupr_ci_top, alpha=.25, color='red')
    axs2[0].set_title('AUPR Bootstrap')
    axs2[1].hist(f1_ci_m[3], bins=100)
    axs2[1].axvline(f1_ci_m[0], color='red')
    axs2[1].axvspan(f1_ci_m[1], f1_ci_m[2], alpha=.25, color='red')
    axs2[1].set_title('Mixed Bias F1 Boostrap')
    axs2[2].hist(f1_ci_b[3], bins=100)
    axs2[2].axvline(f1_ci_b[0], color='red')
    axs2[2].axvspan(f1_ci_b[1], f1_ci_b[2], alpha=.25, color='red')
    axs2[2].set_title('Biased F1 Boostrap')
    fig2.suptitle(title + ' Bootstrap Histograms', fontsize=14)
    fig2.tight_layout()
    fig2.subplots_adjust(top=0.85)
    if save_fname:
        plt.savefig(save_fname+'_bootstrap_hists.pdf')

    return {
        'aupr':aupr,
        'aupr_ci':(aupr_ci_bottom, aupr_ci_top),
        'aupr_samples':samples,
        'mixed_precision':precision_m,
        'mixed_recall':recall_m,
        'mixed_f1':f1_ci_m[0],
        'mixed_f1_ci':f1_ci_m[1:3],
        'mixed_f1_samples':f1_ci_m[3],
        'biased_precision':precision_b,
        'biased_recall':recall_b,
        'biased_f1':f1_ci_b[0],
        'biased_f1_ci':f1_ci_b[1:3],
        'biased_f1_samples':f1_ci_b[3]
    }

def print_model_hyperparams(model, name):
    useful_params = {k:v for k,v in model.get_params().items() if '__' in k}
    print "*** {} Hyperparameters ***".format(name)
    pprint(useful_params)

def precision_at_recall(model, label_key, desired_recall, test_data=None):
    """
    Return the precision, recall, and threshold of a model that comes closest to the `desired_recall` value.
    Additionally, we return the error := true_recall - desired_recall.
    """
    y_trues = np.array(test_data[label_key])
    is_biased = np.array(test_data['is_biased'])
    y_preds = model.predict(test_data['text'])
    y_pred_probs = model.predict_proba(test_data['text'])[:,1]
    ps, rs, ts = importance_weighted_pr_curve(y_trues, y_pred_probs, is_biased)
    closest = sorted(zip(ps, rs, ts), key=lambda x:abs(x[1]-desired_recall))[0]
    return closest + (closest[1]-desired_recall,)

def pr_curves(model_list, title_list, main_title, label_key,
              dashes=[], xlim=(0,1), ylim=(0,1), figsize=(6,4),
              xticks=None, yticks=None,
              save_fname=None, test_data=None):
    """ Plot pr curves for some list of models. """
    y_trues = np.array(test_data[label_key])
    is_biased = np.array(test_data['is_biased'])

    fig, ax = plt.subplots(1,1, figsize=figsize)
    for i, (model, title) in enumerate(zip(model_list, title_list)):
        y_preds = model.predict(test_data['text'])
        y_pred_probs = model.predict_proba(test_data['text'])[:,1]
        ps, rs, ts = importance_weighted_pr_curve(y_trues, y_pred_probs, is_biased)
        dash = dashes[i] if dashes else [1]
        ax.plot(rs, ps, dashes=dash, label='{}'.format(title))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_title(main_title)
    ax.set_xlabel('Recall')
    ax.set_ylabel('Precision')
    if xticks is not None:
        ax.set_xticks(xticks)
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.legend(loc=8)
    if save_fname:
        plt.savefig(save_fname+'_pr_curves.pdf')
    return fig, ax
