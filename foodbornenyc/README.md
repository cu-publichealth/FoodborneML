# FoodbornNYC package

This python package implements the system components used in FoodborneNC system.

It is broken down into subpackages that modularize how the system works to keep things DRY and clear.

## Subpackages

1. [**sources**](#sources)
2. [**models**](#models)
3. [**pipes**](#pipes)
4. [**pipelines**](#pipelines)
5. [**methods**](#methods)
6. [**deployment**](#deployment)
7. [**util**](#util)

### <a name="sources"></a>Sources

`sources` define how to pull data from various sources, such as the Yelp syndication, Twitter, the Web, etc.

Each module in `sources` implements how to connect to some data feed.

These modules interact with `models` to persist raw data feeds into the database to be later analyzed.


### <a name="models"></a>Models

`models` define data models that are used by the system and persisted to the database.

This is done by defining a python class and a mapping to a `Table` with all of the necessary data attributes.

We use the SQLAlchemy library to provide ORM functionality and communicate with the database.
This allows for simpler, more pythonic code and the abstraction from having to write SQL.

Using the ORM also allows for the code to be database agnostic, since SQLAlchemy generates the correct SQL syntax programmatically.

All (with few exceptions) interactions with the database should use the `models` module.  Abstracting out DB code keeps everything clean and allows for modularity.

**NOTE:** In some cases using the ORM can be very slow and custom database interactions may need to be coded.  
W.r.t. this program, it is best to first try and use SQLAlchemy's `core` functionality (one layer below the ORM) to interact with the DB in a way that is still DBMS agnostic.

If totally necessary, writing explicit SQL can be done, but please make note of it here and within the code.

#### Database specific exceptions

1. `yelp_fast.py` in sources uses some SQL strings to enable/disable key constraints to allow for speedup of the yelp feed. 


### <a name="pipes"></a>Pipes

`pipes` define individual components of processing data. This is similar in design to scikit-learn and MALLET (in Java) and should be thought of as analogues to the stateless functions of functional programming, allowing for the DRY modular composition of these individual components for use in `pipelines` discussed below. 

For example, a pipe might define a certain way of tokenizing some input.



### <a name="pipelines"></a>Pipelines



### <a name="methods"></a>Methods



### <a name="deployment"></a>Deployment



### <a name="util"></a>Util




