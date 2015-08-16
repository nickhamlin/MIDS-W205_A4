#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 19:03:10 2015

@author: nicholashamlin
"""

import re

from mrjob.job import MRJob

#same list of hashtags from scrape_tweets.py
teams=['CAN','USA','MEX','CRC','COL','ECU','BRA','CMR','NGA','CIV','ESP','FRA','ENG','NED','GER','SUI','NOR','SWE','CHN','KOR','JPN','THA','AUS','NZL']
teams=[i.lower() for i in teams]

#This is a special case of the word count job, running only on specific words
class MRWordFrequencyCount(MRJob):

    def mapper(self, _, line):
        """Parse words from CSV"""
        tweet=line.split(",")[1].lower()
        tweet=re.sub(r'[^a-z 0-9]','', tweet)
        words=tweet.split()
        for word in words:
            yield word, 1

    def reducer(self, key, values):
        """Sum tweets by word for relevant hashtags"""
        total=sum(values)
        if key in teams: #We only care about team hashtags
            yield key, total

if __name__ == '__main__':
    MRWordFrequencyCount.run()

#To run locally:
#./support_messages.py WC2015.csv

#To run on EMR:
#python support_messages.py -r emr --conf-path mrjob.conf --output-dir s3://hamlin-mids-assignment4/sm_output s3://hamlin-mids-assignment4/input/WC2015.csv
