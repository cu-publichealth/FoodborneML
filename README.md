# FoodborneNYC

![Build Status](https://travis-ci.org/teffland/FoodborneNYC.svg?branch=master)

The new implementation of a system to mine social media documents for evidence of foodborne illness outbreaks in NYC restaurants.

This software will be used by the NYC Department of Health and Mental Hygiene (DOHMH) to inform their practices.

Currently it's just research code.

## For Readers of the code / those just looking over the project


## Install Guide

This install guide is currently just intended for Mac OSX in the Terminal. Note that `< >` encloses things you will need to fill in yourself


1. Make sure you have XCode Commandline tools installed, test this with `gcc` or `make`. If you get a prompt, follow it.

2. If you don't have it, install Homebrew:

    ```bash
    $ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    ```

3. Properly install python with `brew install python`

4. Now you have `pip`. Next install virtualenv and virtualenvwrapper with `pip install virtualenvwrapper`

5. Add the following lines to your `~/.bash_profile`:

    ```bash
    # virtualenv and virtualenvwrapper settings
    export WORKON_HOME=$HOME/.virtualenvs
    source </path/to/wherever/pip/installed/virtualenvwrapper.sh>
    # eg, /Users/thomaseffland/Library/Python/2.7/bin/virtualenvwrapper.sh
    ```
    Make sure to source this file with `source ~/.bash_profile` or by opening a new Terminal window

6. Create a virtualenv to encapsulate the project with:

    ```bash
    cd <~/mydevdir/FoodborneNYC>
    mkvirtualenv fbnyc
    ```

    Note that in the future you'll need to activate the environment with `workon fbnyc` or deactivate it with `deactivate fbnyc`
    
    You'll know that you're in a virtual environment because your command prompt will be prefixed with the environment name, eg.:
    ```bash
    (fbnyc) FoodborneNYC thomaseffland$
    ```

7. Install `git` if you don't have it already with `brew install git`

8. Clone the repository from github with `git clone https://github.com/teffland/FoodborneNYC.git`

9. Install all of the python dependencies

    - If you just want to run the tool as is then use `pip install --upgrade -r deploy_requirements.txt`
    - If you want to develop the code, use `pip install --upgrade -r requirements.txt`
    - You may need to install additional software for the dev requirements, like a Fortran compiler.

10. Congratulations! You now have FoodborneNYC installed. You can start messing with the code. Check out the command line options with `python main.py --help`

11. To start using the data collection sources initialize your database schema with `python main.py initdb`

**NOTE:** Due to the volume of data (even just from Yelp), it is highly recommended that you use a real DBMS instead of the preconfigured sqlite.  SQlite is an in memory database and you are likely to have performance issues. Currently the system has only been tested for MSSQL Server, but SQLAlchemy does support many backends.  For further info look [here](http://docs.sqlalchemy.org/en/latest/dialects/). 



## For Developers of the code

- When commiting, if you want to skip a CI build (eg, if you're just updating a README), make sure to add "[ci skip]" somewhere in your commit message.

### Best Practice References

- Follow [PEP #0008](https://www.python.org/dev/peps/pep-0008/) for style and documentation guidance
- When developing features, we will use a subset of the [Github Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow). It's lightweight and conceptually simple but will encapsulate all of your work.
    * We will maintain two main branches: production and development
    * Production (master) will only be for stable releases
    * Development (dev) will be the main working branch (think of this as master for dev purposes)
    * Everytime you want to build a feature, create a new branch from dev
        * Name your branch explicitly, eg "tom-ui-refactoring"
        * Commit to your branch often
        * Push your local commits to the central repo branch whenever you finish a work-session
    * When you're ready to merge your feature back into dev, issue a pull request
        * We will review your changes and make sure it passes all testing
    * When we are ready to productionalize a version of the dev branch, it'll get merged with master

- I highly suggest using [git-flow](http://danielkummer.github.io/git-flow-cheatsheet/) to make using this workflow super convenient
- We'll use TravisCI for continuous integration on pull requests.  This saves us a lot of work. See [this](http://stackoverflow.com/questions/32422264/jenkins-vs-travis-ci) for an explanation
- Write your unit tests with `pytests`
- Use `pylint` for some helpful automated code review
** TODO (teffland) ** - add testing coverage metrics
- Eventually, we'll use [Sphinx](http://www.sphinx-doc.org/en/stable/) and [ReadTheDocs](https://readthedocs.org/) for automated documentation

#### Some useful references

- A [useful reference](https://www.jeffknupp.com/writing-idiomatic-python-ebook/) for many things python. Specifically on how to write "pythonic" (idiomatic python) code 
- A great resource on python best practices continually updated by python experts: [Hitchhiker's Guide to Python](http://docs.python-guide.org/en/latest/)
