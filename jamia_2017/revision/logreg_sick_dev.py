import numpy.random as npr

from sklearn.externals import joblib

from baseline_experiment_util import setup_baseline_data, random_search
from logreg_model import model

random_seed = 0

data = setup_baseline_data(train_regime='silver', test_regime='silver', random_seed=random_seed)
train_data = data['train_data']
U = data['U']

N = 2
random_hyperparams = {
    'count__ngram_range':[(1,n) for n in npr.randint(1,4, N)],
    'count__max_df':npr.uniform(.9, 1.0, N),
    'tfidf__norm':npr.choice(['l1', 'l2', None], N),
    'tfidf__use_idf':npr.choice([True, False], N),
    'logreg__C':npr.randint(0,200, N),
    'logreg__penalty':npr.choice(['l1', 'l2'], N)
}

score_kwds = {
    'xs':train_data['text'],
    'ys':train_data['is_foodborne'],
    'bs':train_data['is_biased'],
    'U':U,
    'fit_weight_kwd':'logreg__sample_weight',
    'n_cv_splits':3,
    'random_seed':random_seed
}
experiments = random_search(model, random_hyperparams, 'best_logreg.pkl', **score_kwds)
print 'Writing out experiments'
joblib.dump(experiments, 'logreg_hyperparam_experiments.pkl')
print 'All done'