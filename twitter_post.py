"""
Simple script to post tweets with our keywords every few hours
"""
import time
from random import randint

import schedule

from twython import Twython
from twython.exceptions import TwythonError

from foodbornenyc.db_settings import twitter_config

def post_random_keyword(twitter, terms):
    """ Pick a random index and post that term"""
    # turns out twitter doesn't like duplicate tweets, so let's set up 
    # a bot that makes the chances of duplicates considerably lower
    sentences = [
                 "Hmm what to write",
                 "We don't want them to catch our duplicates",
                 "Random string of words",
                 "Blah blah blah blah",
                 "Let's get weird with it",
                 "Twitter duplicate block is dumb!",
                 "Hehe they can't stop us!"
                 ]
    # pick a sentence at random
    sentence_index = randint(0, len(sentences)-1)
    sentence = sentences[sentence_index]
    # now pick a random split to insert the term
    split_sentence = sentence.split(" ")
    insert_index = randint(0, len(split_sentence)-1)
    # pick the term at random
    term_index = randint(0, len(terms)-1)
    term = search_terms[term_index]
    # insert it
    split_sentence.insert(insert_index, term)
    # make the random tweet. 
    # Now we have len(sentences)*sum(num_splits_per_sentence -1)*len(terms) possibilities
    tweet_text = " ".join(split_sentence)
    tweet = "FoodborneNYC Test: %s" % tweet_text 
    try:
        twitter.update_status(status=tweet)
    except TwythonError:
        # try again if we still fail
        post_random_keyword(twitter, terms)
    print "Posted this tweet: %s" % tweet_text



if __name__ == "__main__":
    # the authorization credentials are stored in db settings, which isn't updated to gihub
    twitter = Twython(twitter_config['consumer_key'],
                      twitter_config['consumer_secret'],
                      twitter_config['access_token'],
                      twitter_config['access_token_secret'])

    search_terms = [
        '#foodpoisoning',
        '#stomachache',
        '"food poison"',
        '"food poisoning"',
        'stomach',
        'vomit',
        'puke',
        'diarrhea',
        '"the runs"'
    ]

    post_random_keyword(twitter, search_terms) #test
    schedule.every().hour.do(post_random_keyword,twitter,search_terms)

    # run the continuous program
    while True:
        schedule.run_pending()
        time.sleep(1) # wait one second
