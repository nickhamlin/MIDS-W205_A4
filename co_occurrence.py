#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 19:03:10 2015

@author: nicholashamlin
"""

import re
from itertools import product

from mrjob.job import MRJob

class MRCoOccurrenceCount(MRJob):

    def mapper(self, _, line):
        """Extract pairs of words from each tweet"""
        #Parse tweet from csv, remove non-alphanumeric characters, and create list of words
        tweet=line.split(",")[1].lower()
        tweet=re.sub(r'[^a-z 0-9]','', tweet)
        words=tweet.split()
        pairs=[]

        #Take product of list to come up with all possible pairs of words
        for x,y in product(words,words):
            if x!=y: #ignore situations where a word appears with itself,
                #alphabetize to avoid double-counting duplicate pairs
                result=[x,y]
                result.sort()
                if result not in pairs: #If we don't do this step, we'll double count
                    pairs.append(result)
                    yield (result[0],result[1]),1


    def reducer(self, key, values):
        """Aggregate counts by pair"""
        out=sum(values)
        #Only return pairs we care about, making sure that they're in alphabetical order
        if key in [["japan", "usa"],["champion", "usa"],["champions", "usa"]]:
            yield key, out


if __name__ == '__main__':
    MRCoOccurrenceCount.run()


#To run locally:
# ./co_occurrence.py WC2015.csv

#To run on EMR:
#python co_occurrence.py -r emr --conf-path mrjob.conf --output-dir s3://hamlin-mids-assignment4/co_output s3://hamlin-mids-assignment4/input/WC2015.csv

#Runtime Stats
#Job launched 1027.6s ago, status RUNNING: Running step (co_occurrence.nicholashamlin.20150806.034303.768833: Step 1 of 1)
#Running time was 603.0s (not counting time spent waiting for the EC2 instances)
