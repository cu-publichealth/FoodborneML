"""
The master utilities file

Available utilities:
- get_logger(__name__): get a module logger that prints to STDOUT
- xuni(s): take a string or unicode and convert it utf8 unicode
- xstr(s): take a unicode and convert it to ascii -- could underflow

"""

import logging
import sys
def get_logger(app, level='DEBUG'):
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
    
# NOTE SURE IF THESE ARE TOTALLY ROBUST
# convert NoneTypes , strings, and weird types to unicodes
def xuni(s):
    if not s:
        return u''
    elif type(s) == str:
        return unicode(s, 'utf-8')
    elif type(s) == unicode:
        return s.encode('utf-8')
    else:
        return u''

def xstr(s):
    if not s:
        return ''
    elif type(s) == unicode:
        return s.encode('ascii','replace')
    else:
        return ''

def sec_to_hms(seconds):
    """Return triple of (hour,minutes,seconds) from seconds"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s
