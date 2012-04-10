'''
Created on Mar 21, 2012

@author: robert
'''
import socket
from celery.task import task
from sign_server import board, weather, twitter
from time import time, localtime, strftime
import logging
import sys

logger = logging.getLogger(__name__)

@task()
def updateInfoBoard(foo, bar):
    logger.warning("updateInfoBoard called");
    try:
        sock = board.get_connection()
        board.clear_panel(sock, 4)
        board.write_to_board(sock, 4, 0, 1, strftime("%a, %d %B %I:%M%p", localtime(time())))
        curRowNum = 1

        for row in weather.Weather().getCurrentWeather():
            print row
            board.write_to_board(sock, 4, curRowNum, 3, str(row))
            curRowNum += 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
    finally:
        board.close_connection(sock)

    return 0

@task()
def updateTwitterBoard(foo, bar):
    logger.warning("updateTwitterBoard called")
    try:
        sock = board.get_connection()
        board.clear_panel(sock, 2)
        board.write_to_board(sock, 2, 0, 0, "*************** Tweets ********************************************************")
        curRowNum = 1
        for row in twitter.Twitter().getNewTweets(11, 79):
            board.write_to_board(sock, 2, curRowNum, 0, str(row + ' '))
            curRowNum += 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
    finally:
        board.close_connection(sock)

    return 0

#updateInfoBoard.apply_async(args=[1, 2], expires=60)


@task()
def updateNetworkStatus(foo=0, bar=0):
    #logger.warning("updateNetworkStatus called")
    try:
        sock = None

        servers = [
            dict(name= 'twitter.com' ),
            dict(name= 'google.com' ),
            dict(name= 'cocomsp.com' ),
            dict(name= 'reddit.com' ),
            dict(name= 'facebook.com' ),
            #dict(name= 'expertocrede.com' ),
        ]

        import subprocess
        import re

        def do_ping(addr):
            try:
                cmdStr = "/bin/ping -c 1 %s " % addr
                p = subprocess.Popen(cmdStr, shell=True, stdout=subprocess.PIPE)
                p.wait()
                line = p.stdout.read()
                match = re.search('(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+) ms', line)
                return match.group(1)

            except Exception, e:
                print 'foo ' + str(e)
                return -1

        for s in servers:
            s['delay'] = do_ping(s['name'])

        red = chr(30)
        green = chr(29)
        amber = chr(31)

        sock = board.get_connection()
        curRowNum = 0
        for s in servers:
            msg = s['name'] + ":                             "
            board.write_line_split(sock, 0, curRowNum, 0, msg )

            delayNum = float(s['delay'])
            colorStr = green
            if delayNum > 250:
                colorStr = red
            elif delayNum > 125:
                colorStr = amber

            delayStr = colorStr + str(s['delay']) + "                      "
            board.write_line_split(sock, 0, curRowNum, 20, delayStr )

            curRowNum += 1

    except Exception, e:
        print "Unexpected error:", sys.exc_info()[0]
    finally:
        if sock is not None:
            board.close_connection(sock)

    return 0