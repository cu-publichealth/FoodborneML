# FoodborneNYC

The new implementation of a system to mine social media documents for evidence of foodborne illness outbreaks in NYC restaurants.

This software will be used by the NYC Department of Health and Mental Hygiene (DOHMH) to inform their practices.

Currently it's just research code.

## For Readers of the code / those just looking over the project


## Install Guide

This install guide is currently just intended for Mac OSX in the Terminal. Note that `< >` encloses things you will need to fill in yourself

1. Setup a directory for your project eg, `mkdir <~/mydevdir/FoodborneNYC>`
2. Make sure you have XCode Commandline tools installed, test this with `gcc` or `make`. If you get a prompt, follow it.
3. If you don't have it, install Homebrew:

    ```bash
    $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    ```
4. Properly install python with `brew install python`
5. Now you have `pip`. Next install virtualenv and virtualenvwrapper with `pip install virtualenvwrapper`
6. Add the following lines to your `~/.bash_profile`:

    ```bash
    # virtualenv and virtualenvwrapper settings
    export WORKON_HOME=$HOME/.virtualenvs
    source </path/to/wherever/pip/installed/virtualenvwrapper.sh>
    # eg, /Users/thomaseffland/Library/Python/2.7/bin/virtualenvwrapper.sh
    ```
    Make sure to source this file with `source ~/.bash_profile` or by opening a new Terminal window

7. Create a virtualenv to encapsulate the project with:

    ```bash
    cd <~/mydevdir/FoodborneNYC>
    mymkvirtualenv fbnyc
    ```

    Note that in the future you'll need to activate the environment with `workon fbnyc` or deactivate it with `deactivate fbnyc`

8. Install `git` if you don't have it already with `brew install git`
9. Clone the repository from github with `https://github.com/teffland/FoodborneNYC.git`
10. Install all of the python dependencies

    - If you just want to run the tool as is then use `pip install --user -r deploy_requirements.txt`
    - If you want to develop the code, use `pip install --user -r requirements.txt`
    
11. Congratulations! You now have FoodborneNYC installed. You can start messing with the code. Check out the command line options with `python main.py --help`



## For Developers of the code

- When commiting, if you want to skip a CI build (eg, if you're just updating a README), make sure to add "[ci skip]" somewhere in your commit message.

### Best Practice References

- Follow [PEP #0008](https://www.python.org/dev/peps/pep-0008/) for style and documentation guidance
- When developing features, use the [Github Flow](https://guides.github.com/introduction/flow/index.html). It's lightweight and conceptually simple but will encapsulate all of your work
    1. Basically each feature you develop will be on it's own, explicitly-named branch.
    2. Commit within your own branch often
    3. When you're ready to merge it with `master`, issue a pull request
    4. We will code review your changes and make sure it passes all testing
- We'll use TravisCI for continuous integration on pull requests.  This saves us a lot of work. See [this](http://stackoverflow.com/questions/32422264/jenkins-vs-travis-ci) for an explanation
- Write your unit tests with `pytests`
- Use `pylint` for some helpful automated code review
- Eventually, we'll use [Sphinx](http://www.sphinx-doc.org/en/stable/) and [ReadTheDocs](https://readthedocs.org/) for automated documentation

#### Some useful references

- A [useful reference](https://www.jeffknupp.com/writing-idiomatic-python-ebook/) for many things python. Specifically on how to write "pythonic" (idiomatic python) code 
- A great resource on python best practices continually updated by python experts: [Hitchhiker's Guide to Python](http://docs.python-guide.org/en/latest/)
