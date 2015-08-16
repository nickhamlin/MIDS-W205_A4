# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 22:04:01 2015

@author: nicholashamlin
"""

import json
import csv
import re
from collections import OrderedDict

teams=['CAN','USA','MEX','CRC','COL','ECU','BRA','CMR','NGA','CIV','ESP','FRA','ENG','NED','GER','SUI','NOR','SWE','CHN','KOR','JPN','THA','AUS','NZL']

def write_to_csv(filename,data):
    """write a list of dicts to csv"""
    with open(filename,'wb') as out:
        output = csv.writer(out)
        output.writerow(data[0].keys()) #Write header row
        for row in data:
            try:
                output.writerow(row.values())
            except UnicodeEncodeError: #Exclude Tweets with unicode characters
                continue

if __name__ == '__main__':
    final_output=[]
    for team in teams:
        #Extract raw data from each team's JSON
        with open("#{0}-1.json".format(team),'rb') as f:
            raw_data=json.load(f)

        processed_data=[]
        for i in raw_data:
            #Extract lists of URLs and Hashtags
            urls=[url['url'] for url in i['entities']['urls']]
            hashtags=[ht['text'] for ht in i['entities']['hashtags']]

            #Removes newlines from text
            text=i['text'].replace('\n', ' ').replace('\r', '')

            #Note if tweet was retweeted or not as boolean for easy indexing later
            if i['retweeted']:
                retweeted=1
            else:
                retweeted=0

            #Extract full date, day, and hour from date string to simplify future MR job
            full_date=i['created_at'][:19]+' '+i['created_at'][-4:]
            date=full_date[4:10]
            hour=full_date[11:13]

            #Put all information in ordered dict to make CSV more user friendly
            entry=OrderedDict()
            entry['id']=i['id']
            entry["text"]=re.escape(text)
            entry['screen_name']=i['user']['screen_name']
            entry['created_at']=full_date
            entry['date']=date
            entry['hour']=hour
            entry['retweeted']=retweeted
            #entry['hashtags']=hashtags
            entry['urls']=urls
            processed_data.append(entry)

        #Write results to file - This can be turned off if team-level results aren't needed
        #write_to_csv("#{0}-1.csv".format(team),processed_data)
        final_output=final_output+processed_data

    #Create master file
    write_to_csv('WC20152.csv',final_output)
