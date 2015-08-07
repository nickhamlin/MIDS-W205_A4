#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 19:03:10 2015

@author: nicholashamlin
"""

import re

from mrjob.job import MRJob

class MRCharAverageCount(MRJob):

    def mapper(self, _, line):
        """Parse tweet from csv, remove non-alphanumeric characters, and return
        total number of characters per tweet in k/v pair"""
        tweet=line.split(",")[1].lower()
        tweet=re.sub(r'[^a-z 0-9]','', tweet)
        yield "chars", len(tweet)

    def reducer(self, key, values):
        """aggregate total character count across all tweets, total number of tweets,
        and divide to calculate average"""
        tweet_total=0
        char_total=0
        for i in values: #i represents the number of characters in a given tweet
            tweet_total+=1
            char_total+=i
        yield "average_tweet_length:", char_total/float(tweet_total)

if __name__ == '__main__':
    MRCharAverageCount.run()

#To run locally:
#./character_count.py WC2015.csv

#To run on EMR:
#python character_count.py -r emr --conf-path mrjob.conf --output-dir s3://hamlin-mids-assignment4/char_avg_output s3://hamlin-mids-assignment4/input/WC2015.csv
