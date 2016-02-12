"""
Special file to hold and initialize the constant Metadata object.

This arose because of the need for cyclic dependencies between the model helper `models`
and all of the other model modules, eg. `businesses`, `documents`, `locations`, etc.

It resolves the need to have `models.py` import, say, `locations.py` which import `models.py`
"""
from sqlalchemy import MetaData

# metadata object shared between models
metadata = MetaData()
