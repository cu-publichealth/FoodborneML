from sklearn.cross_validation import StratifiedKFold, StratifiedShuffleSplit
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.grid_search import GridSearchCV

# import data
def run(csvfile=None, pipeline=None, paramgrid=None, nfolds=3, ncores=-1, topk=3, delim=',', gscv_settings=None):
    if not (csvfile and pipeline and paramgrid):
        print "ERROR: Underspecified experiment"
        raise Exception
        
    data = load_data(csvfile, delim)

    # first we need to keep a test set for estimating generalization errors of our final tuned classifier
    train_data, test_data = split_dev_test(data)
    
    # now parameter tune on training data
    #gscv = parameter_search(train_data, pipeline, paramgrid, n_folds=n_folds, gscv_kwargs=gscv_settings)


#     print "RUNNING EXPERIMENTS"
#     preds, true_labels = [], [] 
    
#     for train_indices, test_indices in folds:
#         train_x, train_y = train_data['x'][train_indices], train_data['y'][train_indices]
#         dev_x, dev_y = train_data['x'][test_indices], train_data['y'][test_indices]
#         print "TRAINING"
#         clf = pipeline.fit(train_x, train_y)
#         print "TESTING"
#         pred = pipeline.predict(dev_x)

#         preds.extend(pred)
#         true_labels.extend(dev_y)
        
#     print true_labels[:10]
#     print preds[:10]
#     print "CLASSIFCATION REPORT:"
#     print classification_report(true_labels, preds)
#     print "POSITIVE RECALL:"
#     print pos_recall(true_labels, preds)
#     cm = confusion_matrix(true_labels, preds)
#     plot_confusion_matrix(cm, labels)
    
    
param_grid = {
    'count__ngram_range': [(1,1), (1,2), (1,3)],
    'count__min_df': [1,3,10],
    'count__stop_words': ['english', None],
    'multinb__alpha': np.linspace(0, 1., 4), # get 4 linearly evenly spaced values in the range
    'multinb__fit_prior': [True, False]
}
results = run(csvfile='yelp_mult_data_small.csv', pipeline=pipeline, paramgrid=param_grid, ncores=-1)