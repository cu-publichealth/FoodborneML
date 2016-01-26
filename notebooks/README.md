# Jupyter Notebooks

Often it's much easier to incrementally develop experimental code within an interactive environment; Jupyter notebooks are great for this.

They allow you to create great annotated experiments with markdown cells. You can also view output and plots within the notebooks. 

They're also awesome for tutorials.

## Using foodbornenyc in your notebooks

Since we're developing a package in the neighboring directory, it's pretty likely that you'll want to use modules from that package.  
Especially the data models and processing pipelines.
 
Because of details of the python interpreter, to import these modules you need to append them to an environment variable called the "PYTHONPATH".
iPython uses this variable to look for other directories that contain packages without having to install the package on your "SYSPATH".

This can be done one of a few ways (in order from most temporary to most permanent):

1. Within a notebook you can use:
```python
import sys
sys.path.append('/full/path/to/wherever/you/have/foodbornenyc/installed')
# example: '/Users/thomaseffland/Development/FoodborneNYC'

import foodbornenyc
```
2. During a terminal session you can set the environment variable for just that session:
```bash
(yourenv)$ export PYTHONPATH=$PYTHONPATH:/full/path/to/wherever/you/have/foodbornenyc/installed
```

3. Set it up permamently by including it in your ```~/.bashrc``` (for linux) or ```~/.bash_profile``` (for osx) (I'm not sure about windows):
```bash
export PYTHONPATH=/full/path/to/wherever/you/have/foodbornenyc/installed

**I'd suggest #3 because it'll save you time in the future**

Happy experimenting!
