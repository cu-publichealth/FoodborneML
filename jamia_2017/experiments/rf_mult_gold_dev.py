import numpy as np
import numpy.random as npr
from time import time

from sklearn.externals import joblib

from baseline_experiment_util import setup_baseline_data, random_search
from rf_model import model
from util import hms

random_seed = 0

print 'Getting data...',
data = setup_baseline_data(train_regime='gold', test_regime='silver', random_seed=random_seed)
train_data = data['train_data']
all_B_over_U = data['all_B_over_U']
print 'Done'

N = 500
random_hyperparams = {
    'count__ngram_range':[(1,n) for n in npr.randint(1,4, N)],
    'count__max_df':npr.uniform(.75, 1.0, N),
    'tfidf__norm':npr.choice(['l1', 'l2', None], N),
    'tfidf__use_idf':npr.choice([True, False], N),
    'rf__n_estimators':npr.choice(range(10,200), N),
    'rf__max_features':npr.choice(['log2', 'sqrt'], N)
}

score_kwds = {
    'xs':train_data['text'],
    'ys':train_data['is_multiple'],
    'bs':train_data['is_biased'],
    'all_B_over_U':all_B_over_U,
    'fit_weight_kwd':'rf__sample_weight',
    'n_cv_splits':5,
    'random_seed':random_seed
}

print 'Starting Experiments...'
t0 = time()
experiments = random_search(model, random_hyperparams, 'best_rf_mult_gold.pkl', **score_kwds)
print 'Done {}:{}:{} seconds. Writing out experiments'.format(*hms(time()-t0))
joblib.dump(experiments, 'rf_mult_gold_dev.pkl')
print 'All done'
