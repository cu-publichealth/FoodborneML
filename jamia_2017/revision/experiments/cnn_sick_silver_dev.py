import numpy.random as npr
import numpy as np
import yaml
from chainer_monitor.run_experiment import run_experiment
from chainer_experiment_util import chainer_random_search

base = yaml.load(open('cnn_setup_sick_silver_config.yaml'))
N = 50
random_points = {
    'model_setup':{
        'setup_config':{
            'cnn_ngrams':[range(1,n) for n in npr.choice([2,3,4], N)],
            'cnn_n_filters_per':npr.randint(10,50, N),
            'dropout_prob':npr.uniform(.1,.4, N)
        }
    },
    'trainer_setup':{
        'setup_config': {
            'adam_alpha':npr.uniform(1e-3, 1e-2, N),
            'l2_coef':[10.**e for e in npr.uniform(-3,1, N)]
        }
    }
}

chainer_random_search(base, random_points, N)
