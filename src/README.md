# The Foodborne NYC Columbia API

This docker-compose application implements a web server that provides access to feeds from Yelp and Twitter.

These feeds are used by the NYC Department of Health and Mental Hygiene (DOHMH) to inform their practices.

To be able to run the code you have both Docker and Docker Compose installed. For more information on how to install these follow these links: [Docker](https://www.docker.com/community-edition) and [Docker Compose](https://docs.docker.com/compose/install/).

To run this application do the following: 
 ```bash
    docker-compose build
    docker-compose up
```

It is broken down into the follwoing sub-applications each implemented by a single docker container.

You can find the code for each container in the sub-folders of this directory.

## Containers

1. [**yelp-service**](#yelp-service)
2. [**yelp-classify**](#yelp-classify)
3. [**twitter-service**](#twitter-service)
4. [**twitter-classify**](#twitter-classify)
5. [**flask-app**](#flask-app)
6. [**nginx**](#nginx)
7. [**mongo**](#mongo)

### <a name="yelp-service"></a>yelp-service

`yelp-service` defines how to pull data from Yelp syndication and stores everything in a MongoDB databse.

Data is stored in two collections businesses and reviews. 

Succesfully running this container depends on having the appropriate information in yelp.ini file.

The information in yelp.ini defines the Amazon AWS access information and the S3 bucket location where a Yelp feed can be found.

If you do not have access to such a feed then you should consider not running yelp-service and yelp-classify.  

A simple way to do so is to remove them from the docker-compose.yml

### <a name="yelp-classify"></a>yelp-classify

`yelp-classify` classifies all reviews from the Yelp feed stored in the MongoDB database.

Every newly classified review is added to the yelp_feed collection so that it gets considered by the web server.

### <a name="twitter-service"></a>twitter-service

`twitter-service` defines how to pull data from twitter and stores everything in the MongoDB databse.

Succesfully running this container depends on having the appropriate information in twitter.ini file.

To get more information on how to get credentials for the Public Twitter API follow this link: [Getting Tokens for Twiiter](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens)

### <a name="twitter-classify"></a>twitter-classify

`twitter-classify` classifies the tweets retrieved by the `twiter-service`.

### <a name="flask-app"></a>flask-app

`flask-app` defines the API provided by the `The Foodborne NYC Columbia API` as a Flask web service.

It has 4 endpoints

1. /new/businesses : This endpoint provides access to Yelp businesses with updated information or new classified reviews. 
2. /new/tweets : This endpoint provides access to new classified tweets.
3. /ack/business/{id} : This endpoint is used by client applications to indicate that they received the new information provided by the /new/businesses endpoint for the business indicated by the {id} parameter. After the client application makes such a call, information about the particular business will not be included in the response of the /new/businesses endpoint unless there is a new review or an update to the business information.
4. /ack/tweet/{id} : This endpoint is used by client applications to indicate that they received the tweet indicated by the {id} paramater. After the client application makes such a call, this tweet will not be included in the feed of /new/tweets.

Endpoints /new/businesses and /new/tweets do not return all the new results in a single call. /new/businesses returns at most 100 updated businesses records and /new/tweets returns at most 100 tweets. To retrieve more results the client application should acknowledge the records received via the corresponding /ack/business and /ack/tweet endpoint. After acknowledging the records, making a call to the /new/businesses or /new/tweets endpoint will provide access to up to 100 new records. This process must be repeated until no new results are retrieved.

### <a name="nginx"></a>nginx

The built-in web server provided by Flask is not well suited for production environments. Nginx here is used as a proxy server that forwards the requests to our Flask web server. You can customize the configuration of the nginx server by changing the nginx/conf.d/app.conf file to fit your needs. To enable SSL support you will need to provide your key and certificate in the nginx/ssl folder.

### <a name="mongo"></a>mongo
An unmodified MongoDB image where all the data get stored. The database data get stored in the data folder. 

