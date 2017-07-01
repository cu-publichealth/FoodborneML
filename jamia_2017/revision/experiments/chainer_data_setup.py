import numpy as np

from nltk.tokenize import TweetTokenizer
from sklearn.model_selection import StratifiedShuffleSplit

from vocab import Vocab
from word_vectors import get_pretrained_vectors
from baseline_experiment_util import setup_baseline_data, calc_train_importance_weights

import logging
logging.basicConfig(level=logging.INFO,
    format='[%(levelname)s] %(asctime)s: %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def setup(config):
    # get raw data
    data = setup_baseline_data(train_regime=config['train_regime'])
    train_data, test_data = data['train_data'], data['test_data']
    U = data['U']

    # tokenize the text
    tokenizer = TweetTokenizer()
    if config['lowercase']:
        tokenize = lambda x: [ t.lower() for t in tokenizer.tokenize(x)]
    else:
        tokenize = tokenizer.tokenize
    train_data['text'] = [ tokenize(text) for text in train_data['text'] ]

    # setup vocab and embeddings
    flat_tokens = [ t for text in train_data['text'] for t in text ]
    token_vocab = Vocab(tokens=flat_tokens, min_count=1)
    token_vocab.drop_infrequent()

    token_embeddings = get_pretrained_vectors(token_vocab,
                                              config['pretrained_vectors'],
                                              normed=config['normalize_vectors'],
                                              trim=config['trim_vector_file'])
    # get importance weights for examples
    train_example_weights = calc_train_importance_weights(train_data['is_biased'], U)
    test_example_weights = calc_train_importance_weights(test_data['is_biased'], U)

    # unzip the dataset
    all_data = [ {'xs':token_vocab.seq2idx(train_data['text'][i], as_array=True).astype(np.int32),
                  'is_biased':train_data['is_biased'][i],
                  'weights':train_example_weights[i],
                  'ys':train_data[config['response_key']][i]}
                for i in range(len(train_data['text'])) ]
    test_data = [ {'xs':token_vocab.seq2idx(test_data['text'][i], as_array=True).astype(np.int32),
                  'is_biased':test_data['is_biased'][i],
                  'weight':test_example_weights[i],
                  'ys':test_data[config['response_key']][i]}
                for i in range(len(test_data['text'])) ]

    # split it into train and dev stratifying by bias and label
    splitter = StratifiedShuffleSplit(n_splits=1,
                                      test_size=config['dev_portion'],
                                      random_state=config['split_random_seed'])
    labels = [datum['ys'] for datum in all_data]
    biases = [datum['is_biased'] for datum in all_data]
    stratify_on_these = np.array(['{},{}'.format(y,b) for y,b in zip(labels, biases)])
    train_idx, dev_idx = splitter.split(stratify_on_these, stratify_on_these).next()
    train_data = [ all_data[i] for i in train_idx ]
    dev_data = [ all_data[i] for i in dev_idx]
    logger.info('{} Training examples, {} Dev, {} Test'.format(
        len(train_data), len(dev_data), len(test_data)))
    return {
        'train_data':train_data,
        'dev_data':dev_data,
        'test_data':test_data,
        'token_vocab':token_vocab,
        'token_embeddings':token_embeddings,
        'U':U
    }
