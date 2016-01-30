"""
YelpClassify

This method takes in Yelp reviews and classifies them.  Then persists those classifications to the corresponding doc model
"""
# import importlib #lets you import modules introspectively
from ..settings import yelp_classify_config as config
from sklearn.externals import joblib

class YelpClassify(object):

    def __init__(self):
        # currently assumes module name and pipeline name are the same
        # pipe_module = importlib.import_module("..pipelines.%s" % (pipeline_name))
        # self.pipeline = pipe_module.pipeline
        clf = joblib.load(config['model_file'])

    def classify_all_reviews(self):
        