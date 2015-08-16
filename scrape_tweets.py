# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 07:20:49 2015

@author: nicholashamlin
"""

import json

from bs4 import BeautifulSoup
import mechanize

from connections import connect_to_twitter_user

#Setup Mechanize browser
br = mechanize.Browser()
br.set_handle_robots(True) #Obey robots.txt
br.set_handle_refresh(False)
br.addheaders = [('User-agent', 'Firefox')]

def load_tweets_from_page(response,output_list):
    """Accepts a mechanize browser object and returns list of all tweets+next page of tweets"""
    html=response.read()
    soup=BeautifulSoup(html)
    #Identify and scrape all tweet ids from a single page of results
    tweets=soup.find_all('div',class_='tweet-text')
    new_tweet_ids=[i['data-id'] for i in tweets]
    output_list=output_list+new_tweet_ids
    #Advance forward one page in search results
    response=br.follow_link(text='Load older Tweets')
    return response,output_list

def get_tweet_ids(hashtag,number_to_get):
    """Extracts lists of tweet IDs from advanced search results for a particular team hashtag within the specified date range"""
    #Use mobile site for simpler pagination, only include tweets in English
    url="""https://mobile.twitter.com/search?q=%23FIFAWWC%20%23{0}%20lang%3Aen%20since%3A2015-06-06%20until%3A2015-07-05&s=typd""".format(hashtag)
    response = br.open(url)
    tweet_ids=[]
    counter=1
    for counter in range(1,number_to_get/20): #There are 20 tweets per page, so find how many pages to iterate over
        if counter % 10 == 0: #print semi-infrequent status updates so we know nothing has gotten stuck
            print "loading page "+str(counter)
        try:
            response,tweet_ids=load_tweets_from_page(response,tweet_ids)
            counter+=1
        #If there are no more unscraped results for a given search, the "Load More Tweets" button won't appear
        #and we can use its absence to confirm that we're finished scraping all results.
        except mechanize._mechanize.LinkNotFoundError:
            print "no more tweets!"
            break
    return tweet_ids


##Class for serializing tweets
class TweetSerializer:
   """Simplified version of TweetSerializer class from past assignments for quick json creation"""
   out = None
   first = True
   count = 0
   tweet_count=0

   def start(self,term):
      self.count += 1
      self.tweet_count=0
      fname = "#"+str(term)+"-"+str(self.count)+".json"
      self.out = open(fname,"w")
      self.out.write("[\n")
      self.first = True

   def end(self):
      if self.out is not None:
         self.out.write("\n]\n")
         self.out.close()
         print str(self.out.name)+' completed'
      self.out = None

   def write(self,tweet):
      if not self.first:
         self.out.write(",\n")
      self.first = False
      self.out.write(json.dumps(tweet._json).encode('utf8'))
      self.tweet_count+=1


def gather_full_tweets (ids,term,threshold):
    """given a list of tweet ids, serialize full JSONs for analysis"""
    api=connect_to_twitter_user() #use user connection for better rate limits

    #divide list of tweets into lists of 100 ids each for compatiliby with Tweepy API
    chunks=[ids[x:x+100] for x in xrange(0, len(ids), 100)]
    print "Loading and storing full tweets for "+term
    serializer = TweetSerializer()
    serializer.start(term)
    for chunk in chunks:
        try:
            for tweet in api.statuses_lookup(chunk):
                serializer.write(tweet)
        except KeyboardInterrupt:
            print 'Manually stopping...'
            serializer.end()
            break
        except BaseException as e:
            print 'Error, program failed: '+ str(e)
            break
    serializer.end()

if __name__=="__main__":
    #List of team hashtags to search for
    teams=['CAN','USA','MEX','CRC','COL','ECU','BRA','CMR','NGA','CIV','ESP','FRA','ENG','NED','GER','SUI','NOR','SWE','CHN','KOR','JPN','THA','AUS','NZL']
    for team in teams:
        print "Now getting tweets for "+team
        new_tweets=get_tweet_ids(team,10000) #Set cap of Max 10,000 tweets per query
        gather_full_tweets(new_tweets,team,10000)
