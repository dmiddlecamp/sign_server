'''
Created on Mar 7, 2012
Migrated to Twitter API 1.1 on June 25, 2013 by towynlin (Zachary Crockett)

@author: robert
'''
import os
import random
import re
from rauth import OAuth1Session

class Twitter(object):
    '''
    classdocs
    '''

    lastTweetId = -1

    def __init__(self):
        '''
        Constructor
        '''

    def resetLastTweet(self):
        self.lastTweetId = -1

    def getNewTweets(self, maxRows, maxCharsPerRow):
        session = OAuth1Session(
            os.environ['COCO_TWITTER_CONSUMER_KEY'],
            os.environ['COCO_TWITTER_CONSUMER_SECRET'],
            access_token=os.environ['COCO_TWITTER_ACCESS_TOKEN'],
            access_token_secret=os.environ['COCO_TWITTER_ACCESS_TOKEN_SECRET'])
        params = { 'q': '@CoCoMSP', 'count': 10, 'result_type': 'recent' }
        self.rawResponse = session.get('https://api.twitter.com/1.1/search/tweets.json', params=params)
        jsonResponse = self.rawResponse.json()

        if (self.lastTweetId == jsonResponse['search_metadata']['max_id_str']):
            return [ ]

        self.lastTweetId = jsonResponse['search_metadata']['max_id_str']

        curRowNum = 0
        charsLeft = maxCharsPerRow
        thisRow = ''
        rows = []

        curColor = 2

        for tweet in jsonResponse['statuses']:
            # Build the printable tweet text

            #random colors
            colorStr = chr(29 + (curColor % 3))  #just write the colors in order
            curColor = (curColor + 1)
            tweetBody = tweet['text'].encode('ascii', 'ignore')

            thisTweet = str(colorStr + '@' + tweet['user']['screen_name'] + ': ' + re.sub(' http://[a-zA-Z0-9\./\=\-_?]*', '', tweetBody ) + ' ')
            charsLeft = charsLeft + 1

            while curRowNum < maxRows:
                # Append as much as we can to this row
                thisRow += thisTweet[0: charsLeft]

                if charsLeft <= (self.colorlessLen(thisTweet)):
                    # This tweet was longer than the row allows, so we'll move
                    # on to the next row, if we can...
                    rows.append(thisRow)
                    curRowNum += 1
    
                    if curRowNum >= maxRows:
                        # We're out of rows, get us outta here
                        break
                    else:
                        # Add what we can to this row
                        thisRow = colorStr + thisTweet[charsLeft:maxCharsPerRow]
                        thisTweet = thisTweet[maxCharsPerRow:]
                        charsLeft = maxCharsPerRow - self.colorlessLen(thisRow)
                else:
                    # This was a short tweet, let's just record it and move on
                    # to the next row
                    charsLeft -= len(thisTweet)
                    break

        return rows

    def colorlessLen(self, string):
        return len(string) - string.count(chr(29)) - string.count(chr(30)) - string.count(chr(31))
