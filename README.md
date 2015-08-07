# Nick Hamlin - Assignment 4

## 1. Summary of Outputs:
### 1.1 Code Files
- **scrape_tweets.py**: Gathers historical tweets by scraping IDs off of advanced search results then querying Twitter API to get actual content of tweets based on IDs
- **process_tweets_to_csv.py**: Strips out unnecessary tweet metadata and consolidates results into the required CSV for MapReduce processing and indexing.
- **connections.py**: Defines functions for connecting to twitter and AWS in one file, which means that credentials need only be stored in one place.
- **word_count.py**: Runs MapReduce job to identify all words appearing more than 10,000 times in the corpus
- **hour_count.py**: Runs MapReduce job to determine the number of tweets for each hour represented in the corpus
- **url_count.py**: Identifies the 20 most commonly tweeted URLs across the corpus
- **co_occurrence.py**: Determines how frequently certain pairs of words appear with each other across all tweets.
- **character_count.py**: Calculates average number of characters per tweet
- **support_messages.py**: Counts number of occurrences of each team-specific hashtag.
- **mrjob.conf**: Defines EMR cluster configuration and bootstrap actions required to support execution of MapReduce jobs.
- **get-pip.py**: A prepackaged version of Pip for easy installation on the EMR cluster, recycled from Assignment 1.
- **index_tweets.py**: Processes tweets for easy searching and uses Whoosh to create index via AsyncWriter class.
- **query_tweets.py**: Defines framework for querying the index created by index_tweets.py and runs four example queries.

### 1.2 Supporting Files
#### On S3:
- **WC2015.csv** The complete collection of tweets and associated metadata.  *Not included in this repo, but available on S3 [here](https://s3-us-west-2.amazonaws.com/hamlin-mids-assignment4/input/WC2015.csv).*
- **tweetindex.zip** Contains index of collected tweets.  For convenience, the entire folder has been compressed into a single .zip file. Available on S3 [here](https://s3-us-west-2.amazonaws.com/hamlin-mids-assignment4/tweetindex.zip).

#### On Github:
- **support_message_results.txt**: Contains the complete count of support messages for each team hashtag.
- **top_urls.txt**: List of top 20 urls across all tweets
- **links_to_mr_job_outputs.txt**: List of direct links to result files each for the MapReduce jobs on S3.  The top-level bucket with everything is available [here](https://s3-us-west-2.amazonaws.com/hamlin-mids-assignment4)

### 1.3 Answers to Specific Assignment Questions
- There are 13 different words that appear at least 10,000 times in the tweet corpus
- The average length (in characters) of all tweets collected is: 75.9126
- Unsurprisingly, the USA hashtag received the most support messages with 16844 across the corpus.
- *USA* occurs with *Japan* 161 times
- *champion* occurs with *USA* 5 times, but *champions* occurs with *USA* 44 times.

## 2. Program Design
### 2.1 Tweet Collection and Storage
Since this assignment requires the collection of tweets further than one week back in time, simply querying the search API is inadequate.  However, the Twitter advanced search page will return results further back in time and allows more detailed search parameters (like only returning tweets in English).  Running a web scraper on this page yields the tweets we care about.  One of the challenges in scraping this page is effectively dealing with the pagination, which on the desktop site is handled by AJAX calls that create an "infinite scroll".  To simplify this process, I instead scraped the mobile version of the search results page, which doesn't require any complex AJAX work and instead just requires clicking a simple "load more tweets" link to gather the next page of information. The Mechanize package for python makes iterating through these pages by clicking the link a simple task.  

Once each page is loaded, I use the Beautiful Soup (BS4) module to extract the unique ID of each tweet from the page's HTML. I chose to scrape just the ID from the search results to minimize the load on twitter's servers through this atypical channel.  After the IDs are gathered, I then use the API's statuses_lookup method to collect the full data of the tweets.  This approach has several benefits.  First, it scales easily to allow for gathering of any interesting data about the tweet, not just what appears on the search results.  It's also more robust over the long term.  If Twitter changes the construction of its results page, it would require a complete rewrite of a scraper that gathered all tweet information directly.  However, since this approach requires scraping the IDs only, it's much more easily fixed should the results page change in the future.

The program will gather up to approximately 10,000 tweets for each hashtag, though this threshold can be changed easily.  Many of the hashtags yield fewer than 10,000 search results (since teams are eliminated early and/or have fewer users tweeting in English). In total, I gathered 94,174 tweets across all hashtags. Once the tweets are collected and serialized, all unnecessary metadata is discarded and only the information needed for the remaining analysis is combined into WC2015.csv.  This conversion step allows for some preprocessing of the data that simplifies both the MapReduce jobs and the index creation, as well as the removal of tweets with unicode characters.  After this processing step, 83,184 tweets remained for analysis.

### 2.2 Data Analysis via EMR
#### 2.2.1 MapReduce Job Design
The MapReduce jobs are run on Amazon Elastic Map Reduce (EMR) via the Python MRJob module.  MRJob is a convenient choice for this implementation because it allows for easy packaging of each job, including all necessary map, shuffle, and reduce steps, into a single script that can be run both locally for testing and deployed to the cluster. To do this, I extend the MRJob class to include custom methods specific to the question the job is answering.  While the specifics of each method vary slightly from job to job are are explained in greater detail in the comments that accompany each file, in general the map step processes each line from the source data into the relevant partitions and yields key-value pairs for each unit of analysis (for example, keys are individual words for word_count.py, but tuples containing pairs of words for co_occurrence.py). The reduce step aggregates these results and performs any other required operations (like dividing to find an average in the case of character_count.py).

Since these jobs can output large lists of data, I use the reduce step to limit the results for jobs where we're interested in particular data points.  For example, instead of listing all possible pairs of words, the co-occurrence job will only return the selection of pairs that we care about.  This makes extracting the answer to the question much simpler than if we had to wade through a massive list of results.  In each case, these filters can be easily adjusted if different questions are asked in the future.

In some cases, like in calculating the list of the top 20 urls, an additional reduce step is needed to sort the results before the relevant subset are returned.  Thankfully, MRJob makes adding these additional steps simple, which is why it makes more sense to implement these jobs than writing separate map and reduce files for each and manually running them through EMR.

#### 2.2.2 EMR Cluster Configuration
These jobs are run on an EMR cluster consisting of one master and one slave node, each an m1.medium machine in the US-West-2 region running Amazon Linux AMI Version 3.0.4 and Python 2.7.  Some simple bootstrap actions (defined in mrjob.conf) also install mrjob, pip, and boto for easy interaction with S3. This certainly isn't the most powerful configuration possible, but it's certainly adequate to run these problems and minimize costs.  While I considered the use of spot instances to further minimize costs, I ultimately decided against using them.  The particular instances making up the EMR cluster are inexpensive enough on their own that the decrease in MR job runtime caused by using standard instances is worth the slight increase in cost. On this cluster, the jobs used to answer the questions above typically ran from start to finish in 10-15 minutes, including provisioning of EC2 capacity, software configuration, bootstrap actions, and actual job execution. Input data for each job is read directly in from S3, which speeds up job setup time.

### 2.3 Indexing and searching
#### 2.3.1 Schema Design
Using Whoosh's Schema and AsyncWriter classes, I indexed the tweets along the following criteria
- Text
- Screen name of user sending the Tweet
- Date and time of tweet creation (stored as a Python Datetime object)
- Whether the tweet is original or a retweet of existing content (stored as a boolean)
- Keywords related to the text of the Tweet (stored as a space delimited string of words)

Both standard NLTK english stopwords are excluded when defining the keywords, as well as a custom list of twitter-specific jargon stopwords (like "ht", "mt", etc.).  The resulting index is just over 80MB and is stored in a directory called "tweetindex"

#### 2.3.2 Querying Process and Example Supported Queries
I used the QueryParser class to provide a more "plain English" UI for querying the tweet index that doesn't require direct use of the more complex Whoosh query construction.  Running query_tweets.py will automatically run a few example queries along all the different components of the schema.  They are:

- search("Jackman"): tweets mentioning Hugh Jackman in the text
- search("keyword:Jackman OR screen_name:BBCSport"): tweets mentioning Hugh Jackman as a Keyword or created by BBCSports account
- search("Lionesses AND contains_retweet:True"): Retweeted tweets about the English Team
- search("inspiring AND created:2015061800"): Tweets between 12-1am on June 18 containing the word "inspiring"
- search("screen_name:BBCSport AND contains_retweet:False"): Original tweets by BBCSports account

While the plain text and keyword search parameters are similar in both composition and results, the keyword search is optimized for faster performance by removing unnecessary words and punctuation that don't contribute meaningfully to the relevant components of the tweets.

In addition, running `from query_tweets import search` allows searches to be run directly from the command line if preferred.

## 3.Packages used
#### Base Python:
- json
- os
- re
- csv
- collections (OrderedDict class)
- datetime

#### Third Party:
- Mechanize (for interaction with webpages)
- BeautifulSoup (BS4)
- Tweepy
- MRJob
- Whoosh
- NLTK (for word tokenization and stopword exclusion)

## 4.Other Useful References:
- http://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet
- http://mrjob.readthedocs.org/en/latest//en/latest/job.html#multi-step-jobs
- https://github.com/Yelp/mrjob/blob/master/mrjob/examples/
- http://stackoverflow.com/questions/2550784/sorted-word-count-using-hadoop-mapreduce
