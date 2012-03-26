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
    lastTweetId = 176856173172097026;
#    maxCharsPerRow = 80
#    maxRows = 6


    def __init__(self):
        '''
        Constructor
        '''


    def getNewTweets(self, maxRows, maxCharsPerRow):
        jsonResponse = json.loads(urllib.urlopen(self.twitterBaseUrl).read())
        self.lastTweetId = jsonResponse['max_id_str']

        curRowNum = 0
        charsLeft = maxCharsPerRow
        thisRow = ''
        rows = []

        curColor = 2

        for tweet in jsonResponse['results'].__iter__():
            # Build the printable tweet text

            #random colors
            #colorStr = "{#" + str(random.randint(0, 2)) + "}"

            #colorStr = "{#" + str(curColor % 3) + "}"  #markup
            colorStr = chr( 29 + (curColor%3))  #just write the colors in order
            curColor = (curColor + 1)

            thisTweet = colorStr + '@' + tweet['from_user'] + ': ' + re.sub(' http://[a-zA-Z0-9\./\=\-_?]*', '', tweet['text']) + '  '

            while curRowNum < maxRows:
                # Append as much as we can to this row
                thisRow += thisTweet[0: charsLeft]

                if charsLeft <= len(thisTweet):
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
                        charsLeft = maxCharsPerRow - len(thisRow)
                else:
                    # This was a short tweet, let's just record it and move on
                    # to the next row
                    charsLeft -= len(thisTweet)
                    break

        return rows
