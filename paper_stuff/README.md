# Basic Info
## Notebooks/

Contains the ipython notebooks. I added pretty much everything under the sun here, but you should really only need two files:
 - **Mult_ROC_LogReg_Final.ipynb** : Everything for generating the **Multiple** classifier, comparing AUC to old classifier's, identifying threshold (Youden's J), plotting roc curve, writing feature weights and test prediction scores to csvs
 - **Sick_ROC_LogReg_Final.ipynb** : Same as above for the **Sick** classifier, minus the threshold stuff

**NOTE:** The encoding stuff for the old data vs the new data is bit weird--basically, in **load_data** for each file, there are two ways of dealing with data['x']. I've labelled one as for the "old classifier auc" (e.g. for calculating auc of old classifier using old_predictions, true_labels as data['x'], data['y']), and the other for "generating new classifier" (e.g. for making a new classifier using reviews, true_labels as data['x'], data['y']). So just comment out the one you don't want and everything should run just fine

## data/
- **all_data_from_dohmh.xlsx** contains everything from dohmh, for all ~8000 reviews (this is just a renamed version of the "yelp data for Fotis XXXX" version thats floating around somewhere else in the foodborne repo
- **TrainingDataAllValues.xlsx** contains everything from dohmh, but **only** for the training data (~1300 reviews).
- **Mult/** contains everything for the **Multiple** classifier, including training data, old classifier test predictions, new classifier test predictions and feature weights, etc. I tried to rename things more intuitively for you guys, but let me know if you have any questions! The "_small" versions of certain files contain the ~1300 reviews used for development
- **Sick/** same as above for the **Sick** classifier

##best_classifiers/
Contains the top **Sick** and **Multiple** classifiers
