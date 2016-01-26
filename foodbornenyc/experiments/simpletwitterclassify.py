from ..pipelines.simpletwitter import pipeline

from sklearn.cross_validation import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score
import numpy as np

# import data
def run(csvfile, pipeline, paramarray):
    import csv
    data = []
    with open('foodbornenyc/experiments/training_chi_dohmh_tweets.csv', 'r') as f:
        reader = csv.reader(f, delimeter=",")
        print "HEADERS: ", reader.next()
        for row in reader:
            data.append((unicode(row[0], 'utf-8'), row[1]))
    data = np.array(data)
    labels = data[:,1]
   # print "LABELS: ", labels

    folds = StratifiedKFold(labels, n_folds=3, random_state=0,shuffle=False)

    print "RUNNING EXPERIMENTS"
    preds, true_labels = [], []

    # testing a sinle 66:33 split
    # train_indices, test_indices = [ fold for fold in folds][0]
    # data_train_X, data_train_Y = data[train_indices, 0], data[train_indices, 1]
    # data_test_X, data_test_Y = data[test_indices, 0], data[test_indices, 1]
    # #print list(data_train_X[:5])
    # print "TRAINING"
    # clf = pipeline.fit(data_train_X, data_train_Y)
    # print "TESTING"
    # pred = pipeline.predict(data_test_X)

    # preds.extend(pred)
    # true_labels.extend(data_test_Y)   

    for train_indices, test_indices in folds:
        data_train_X, data_train_Y = data[train_indices, 0], data[train_indices, 1]
        data_test_X, data_test_Y = data[test_indices, 0], data[test_indices, 1]
        #print list(data_train_X[:5])
        print "TRAINING"
        clf = pipeline.fit(data_train_X, data_train_Y)
        print "TESTING"
        pred = pipeline.predict(data_test_X)

        preds.extend(pred)
        true_labels.extend(data_test_Y)
    cm = confusion_matrix(true_labels, preds)
    print "CONFUSION MATRIX:"
    print cm
    print "CLASSIFICATION REPORT:"
    print classification_report(true_labels, preds)
    print "ACCURACY:"
    print accuracy_score(true_labels, preds)

