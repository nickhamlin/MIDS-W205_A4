# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 14:27:45 2015

@author: nicholashamlin
"""

import pymongo
import tweepy
from boto.s3.connection import S3Connection

#tweepy
def connect_to_twitter_app():
    consumer_key = "<CONSUMER_KEY>";
    consumer_secret = "<CONSUMER_SECRET>";
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth_handler=auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,timeout=300)
    return api

def connect_to_twitter_user():
    consumer_key = "<CONSUMER_KEY>";
    consumer_secret = "<CONSUMER_SECRET>";
    access_token = "<ACCESS_TOKEN>";
    access_token_secret = "<ACCESS_TOKEN_SECRET>;
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth_handler=auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,timeout=300)
    return api

def connect_to_mongo():
    try:
        conn=pymongo.MongoClient()
        print "Connected!"
        return conn
    except pymongo.errors.ConnectionFailure, e:
       print "Connection failed : %s" % e

def connect_to_s3():
    conn = S3Connection('<AWS_ACCESS_KEY_ID>', '<AWS_ACCESS_SECRET>')
    return conn
