from weighted_loss_model import WeightedLossModel
from cbow_model import TextCBOW

def setup(config, data_setup_results):
    predictor_model = TextCBOW(data_setup_results['token_embeddings'],
                               config['composition_func'])
    loss_model = WeightedLossModel(predictor_model)
    return {
        'predictor_model': predictor_model,
        'loss_model': loss_model
    }
