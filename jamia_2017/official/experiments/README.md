# Experiments

This folder contains the supporting code for `../Offical\ Results.ipynb`.

`baseline_experiment_util.py` has all of the functions used in the offical results.

`best_models` has the final best models from each experiment regime used in the official results.

**NOTE** that before `../Offical\ Results.ipynb` can be run, the models need to be unzipped with `gunzip -v best_models/*`

The other files are the model definitions and hyperparam search experiments:

`<Models>`:
* `lr` == Logistic Regression
* `rf` == Random Forest
* `svm` == SVM

`<model>_model.py` contains the model definitions

`<model>_<task>_<regime>_dev.py` contain the hyperparam search experiments

`launch_<model>_dev.sh` are bash scripts for running the experiments by model type,

To actually be able to run the experiments you need the data, which can be requested from [Tom Effland](mailto:teffland.cs.columbia.edu).
