# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 16:08:59 2015

@author: nicholashamlin
"""
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser.dateparse import DateParserPlugin

index = open_dir("tweetindex")
searcher = index.searcher()

#Use QueryParser to make entering queries easier
parser = QueryParser("text", index.schema)
#Dates should be coded as strings of integers in this plugin
#For example, 11:30 AM on March 5, 2015 would be 201503051130
parser.add_plugin(DateParserPlugin())

def search(search_string):
    query=parser.parse(search_string)
    print "searching for..."+search_string
    results = searcher.search(query)
    print '# of hits:', len(results)
    if len(results)>0:
        print 'Best Match:', results[0]
    else:
        print 'Please try a different query'
    print '\n'
    return results

if __name__=='__main__':
    #EXAMPLE QUERIES
    search("Jackman") #tweets mentioning Hugh Jackman in the text
    search("keyword:Jackman OR screen_name:BBCSport") #tweets mentioning Hugh Jackman as a Keyword or created by BBCSports account
    search("Lionesses AND contains_retweet:True") #Retweeted tweets about the English Team
    search("inspiring AND created:2015061800") #Tweets between 12-1am on June 18 containing the word "inspiring"
    search("screen_name:BBCSport AND contains_retweet:False") #Original tweets by BBCSports account

