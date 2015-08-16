# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 16:01:39 2015

@author: nicholashamlin
"""
import csv
import datetime

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from whoosh.fields import Schema, ID, TEXT, KEYWORD, DATETIME, BOOLEAN
from whoosh.index import create_in
from whoosh.writing import AsyncWriter

#Define both default and Twitter-specific stopwords for exclusion 
default_stops = (stopwords.words("english"))
custom_stops=['rt','ht','mt','@','#','!',':',';',',','.',"'s","?","\\n",'http','https',"n't","&","\\",'...','-','"']
stops=list(set(default_stops+custom_stops))

#Set up schema fields
my_schema = Schema(id = ID(unique=True, stored=True),
                    text = TEXT(stored=True),
                    contains_retweet= BOOLEAN(stored=True),
                    screen_name = TEXT(stored=True),
                    keyword=KEYWORD(stored=True),
                    created=DATETIME(stored=True)
                    )


#Create index and AsyncWriter object
index = create_in("tweetindex", my_schema)
writer = AsyncWriter(index)

if __name__=='__main__':
    #Load raw data
    with open("WC2015_headers.csv",'rb') as to_load:
        data=csv.DictReader(to_load)
        for row in data:
            #Extract required information from date to create python datetime object
            date=row['created_at'][:19]+' '+row['created_at'][-4:]
            
            #Clean text and parse into keywords
            text=row['text'].replace('\\','')
            keywords=[word for word in word_tokenize(text) if word not in stops]
            
            #Check for Retweets
            rt=False
            if 'RT ' in text:
                rt=True
            
            #Add completed document to index
            writer.add_document(id = unicode(row['id']), 
                                screen_name = unicode(row['screen_name']),
                                text = unicode(text),
                                contains_retweet=rt,
                                keyword = unicode(" ".join(keywords)),
                                created = datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y")
                                )
        writer.commit()