#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 19:03:10 2015

@author: nicholashamlin
"""

import re

from mrjob.job import MRJob

class MRTweetHourlyCount(MRJob):
    def mapper(self, _, line):
        """Parse date and hour from csv, which have been stored separately to
        make this step simple"""
        tweet=line.replace("\,","")
        tweet=tweet.split(",")
        date=tweet[4]
        hour=tweet[5]
        #Return date/hour tuple as key
        yield (date,hour),1

    def reducer(self, key, values):
        """Aggregate results by date/hour"""
        out=sum(values)
        yield key, out

if __name__ == '__main__':
    MRTweetHourlyCount.run()

#To run locally:
#./hour_count.py WC2015.csv

#To run on EMR:
#python hour_count.py -r emr --conf-path mrjob.conf --output-dir s3://hamlin-mids-assignment4/hc_output s3://hamlin-mids-assignment4/input/WC2015.csv

#Runtime Stats:
#Job launched 560.3s ago, status RUNNING: Running step (hour_count.nicholashamlin.20150806.040555.417749: Step 1 of 1)
#Running time was 103.0s (not counting time spent waiting for the EC2 instances)
