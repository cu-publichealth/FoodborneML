#!/bin/bash

if [[ $1 == "import" ]]; then
    mongoimport --host $HOST --port $PORT --db $DB --collection Restaurants --file $RESTAURANTSFILE
    mongoimport --host $HOST --port $PORT --db $DB --collection Reviews --file $REVIEWSFILE
fi

mongo $HOST:$PORT --eval "var dbName = '$DB'" initdb.js

