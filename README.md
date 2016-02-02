# FoodborneNYC

The new implementation of a system to mine social media documents for evidence of foodborne illness outbreaks in NYC restaurants.

This software will be used by the NYC Department of Health and Mental Hygiene (DOHMH) to inform their practices.

Currently it's just research code.

## For Readers of the code / those just looking over the project


## For Developers of the code


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
