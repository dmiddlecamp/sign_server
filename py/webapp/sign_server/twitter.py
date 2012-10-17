'''
Created on Mar 7, 2012

@author: robert
'''
import json
import random
import re
import urllib

class Twitter(object):
    '''
    classdocs
    '''

    twitterBaseUrl = "http://search.twitter.com/search.json?q=%40CoCoMSP&rpp=10&result_type=recent"
    #twitterBaseUrl = "http://search.twitter.com/search.json?q=%23aam40years&rpp=10&result_type=recent"
#    twitterBaseUrl = "http://api.twitter.com/1/lists/statuses.json?slug=coco-members&owner_screen_name=CoCoMSP&page=1&per_page=10"
    lastTweetId = -1
#    maxCharsPerRow = 80
#    maxRows = 6


    def __init__(self):
        '''
        Constructor
        '''

    def resetLastTweet(self):
        self.lastTweetId = -1

    def getNewTweets(self, maxRows, maxCharsPerRow):
        self.rawResponse = urllib.urlopen(self.twitterBaseUrl).read()
        jsonResponse = json.loads(self.rawResponse)

        if (self.lastTweetId == jsonResponse['max_id_str']):
            return [ ]

        self.lastTweetId = jsonResponse['max_id_str']

        curRowNum = 0
        charsLeft = maxCharsPerRow
        thisRow = ''
        rows = []

        curColor = 2

        for tweet in jsonResponse['results'].__iter__():
            # Build the printable tweet text

            #random colors
            colorStr = chr(29 + (curColor % 3))  #just write the colors in order
            curColor = (curColor + 1)
            tweetBody = tweet['text'].encode('ascii', 'ignore')

            thisTweet = str(colorStr + '@' + tweet['from_user'] + ': ' + re.sub(' http://[a-zA-Z0-9\./\=\-_?]*', '', tweetBody ) + ' ')
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
