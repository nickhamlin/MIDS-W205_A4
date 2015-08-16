#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 19:03:10 2015

@author: nicholashamlin

"""

import re
import csv
import operator

from mrjob.job import MRJob
from mrjob.step import MRStep

output = []

class MRTweetURLCount(MRJob):

    def mapper(self, _, line):
        """Parse list of URLs from csv"""
        split_line=line.split(",")
        x=csv.reader(split_line) #csv module is used to ensure commas in tweets don't break things
        #unpack nested lists and get string of urls
        url_string=list(x)[-1][0]
        url_string=url_string[1:-1]
        urls=url_string.split(" ")
        #once list of URLs is parsed, create k/v pairs
        for url in urls:
            yield url,1

    def combiner(self, key, values):
        """Count total appearances of each URL"""
        out=sum(values)
        if key!="": #ignore tweets that contain no URLs
            yield key, out

    def reducer(self, key, counts):
        """aggregate totaled results to a list for easy sorting"""
        output.append((key, sum(counts)))

    def reducer_final(self):
        """Sort list of results by URL frequency and return top 20 results"""
        map(operator.itemgetter(1), output)
        sorted_results = sorted(output, key=operator.itemgetter(1), reverse=True)
        for result in sorted_results[:20]:
            yield result

if __name__ == '__main__':
    MRTweetURLCount.run()

#To run locally:
#./url_count.py WC2015.csv

#To run on EMR
#python url_count.py -r emr --conf-path mrjob.conf --output-dir s3://hamlin-mids-assignment4/url_output s3://hamlin-mids-assignment4/input/WC2015.csv

#Runtime stats
#Job launched 497.5s ago, status RUNNING: Running step (url_count.nicholashamlin.20150807.212514.805363: Step 1 of 1)
#Running time was 103.0s (not counting time spent waiting for the EC2 instances)
