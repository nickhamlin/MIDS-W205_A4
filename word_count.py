#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 19:03:10 2015

@author: nicholashamlin
"""

import re

from mrjob.job import MRJob

class MRWordFrequencyCount(MRJob):

    def mapper(self, _, line):
        """Parse tweets from input, remove non-alphanumeric characters
        and return key,value pair for each word"""
        tweet=line.split(",")[1].lower()
        tweet=re.sub(r'[^a-z 0-9]','', tweet)
        words=tweet.split()
        for word in words:
            yield word, 1

    def reducer(self, key, values):
        """Aggregate total instances of words, and only return those that appear
        more than 10,000 times"""
        total=sum(values)
        if total>10000: #put cutoff here
            yield key, total

if __name__ == '__main__':
    MRWordFrequencyCount.run()

#To run locally:
#Simple version: ./word_count.py WC2015.csv
#Hadoop version: python absolutize_path.py < WC2015.csv | python word_count.py -r local --conf-path mrjob.conf --no-output --output-dir out

#To run on EMR:
#python word_count.py -r emr --conf-path mrjob.conf --output-dir s3://hamlin-mids-assignment4/wc_output s3://hamlin-mids-assignment4/input/WC2015.csv

#Runtime Stats:
#Job launched 533.9s ago, status RUNNING: Running step (word_count.nicholashamlin.20150806.021938.614588: Step 1 of 1)
#Running time was 139.0s (not counting time spent waiting for the EC2 instances)
