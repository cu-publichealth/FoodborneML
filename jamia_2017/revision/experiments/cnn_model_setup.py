from weighted_loss_model import WeightedLossModel
from cnn_model import TextCNN

def setup(config, data_setup_results):
    predictor_model = TextCNN(data_setup_results['token_embeddings'],
                              config['cnn_n_filters_per'],
                              config['cnn_ngrams'],
                              config['cnn_pooling'],
                              config['cnn_activation_func'])
    loss_model = WeightedLossModel(predictor_model)
    return {
        'predictor_model': predictor_model,
        'loss_model': loss_model
    }
