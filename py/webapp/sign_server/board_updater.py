'''
Created on Mar 21, 2012

@author: robert
'''
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
    logger.warning("updateTwitterBoard called");
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
