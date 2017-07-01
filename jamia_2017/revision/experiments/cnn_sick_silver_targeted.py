import numpy.random as npr
import numpy as np
import yaml
from chainer_monitor.run_experiment import run_experiment
from chainer_experiment_util import chainer_random_search

base = yaml.load(open('cnn_setup_sick_silver_config.yaml'))
N=10
# basically just vary number of filters and l2 coef, and dropout slightly
targeted_points = {
    'model_setup':{
        'setup_config':{
            'cnn_ngrams':[[1,2,3]]*N,
            'cnn_n_filters_per':npr.choice([25,50], N),
            'dropout_prob':npr.uniform(.2,.4, N)
        }
    },
    'trainer_setup':{
        'setup_config': {
            'adam_alpha':[.001]*N,
            'l2_coef':npr.choice(np.logspace(-3,-1,1000), N)
        }
    }
}

chainer_random_search(base, targeted_points, N)
