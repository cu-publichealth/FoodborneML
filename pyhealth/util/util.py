"""
The master utilities file

Available utilities:
* The logger: getLogger()

"""

import logging
import sys
def getLogger(app, level='DEBUG'):
    """
    A system level wrapping of the python logging class to make getting a logger take one function call

    Args:
        app: The name of the app requesting the logger. Will typically be ``__name__``

    Notes:
    * Will probably add in more wrappers in future
    """
    # set up the logger to STDOUT
    logging.basicConfig(stream=sys.stdout, level=level)
    logger = logging.getLogger(app)
    return logger
    