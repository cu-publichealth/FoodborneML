"""
Simple script to post tweets with our keywords every few hours
"""
import time
import schedule
from twython import Twython
from foodbornenyc.db_settings import twitter_config
from random import randint

def post_random_keyword(twitter, terms):
    """ Pick a random index and post that term"""
    term_index = randint(0, len(terms)-1)
    tweet_text = "FoodborneNYC Test: %s" % search_terms[term_index]
    twitter.update_status(status=tweet_text)



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

    # post_random_keyword(twitter, search_terms) #test
    schedule.every(2).hour.at("23:00").do(post_random_keyword(twitter,search_terms))

    # run the continuous program
    while True:
        schedule.run_pending()
        time.sleep(1) # wait one second
