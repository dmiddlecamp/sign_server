'''
Created on Mar 21, 2012

@author: robert
'''
from celery.task import task
from sign_server import board, weather, twitter, announcements
from sign_server.models import Announcement
from time import time, localtime, strftime
import logging
import sys

logger = logging.getLogger(__name__)

@task()
def updateInfoBoard(foo, bar):
    logger.warn("updateInfoBoard called");
    weatherRows = weather.Weather().getCurrentWeather()
    try:
        sock = board.get_connection()
        board.clear_panel(sock, 4)
        board.write_to_board(sock, 4, 0, 1, strftime("%a, %d %B %I:%M%p", localtime(time())))
        curRowNum = 1

        for row in weatherRows:
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
    logger.warn("updateTwitterBoard called");
    twitterRows = twitter.Twitter().getNewTweets(11, 79)
    try:
        sock = board.get_connection()
        board.clear_panel(sock, 2)
        board.write_to_board(sock, 2, 0, 0, "*************** Tweets ********************************************************")
        curRowNum = 1
        for row in twitterRows:
            board.write_to_board(sock, 2, curRowNum, 0, str(row + ' '))
            curRowNum += 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
    finally:
        board.close_connection(sock)

    return 0

@task()
def updateAnnouncementBoard(foo, bar):
    logger.warn("updateAnnouncementBoard called")
    try:
        sock = board.get_connection()
        board.clear_panel(sock, 3)
        board.write_to_board(sock, 3, 0, 0, " - - - - - - - - - - - - - - - - Announcements - - - - - - - - - - - - - - - -  ")
        curRowNum = 1
        announcements = list(Announcement.objects.order_by('-creation_date'))
        for announcement in announcements:
            color = chr(29)
            if announcement.priority == 'M':
                color = chr(31)
            elif announcement.priority == 'H':
                color = chr(30)

            row = " " + announcement.announcement_text

            while len(row) < 66:
                # add some padding spaces
                row = row + " "
            row = row + " " + announcement.creation_date.strftime("%a %I:%M%p")
            while len(row) < 81:
                row = row + " "
            board.write_to_board(sock, 3, curRowNum, 0, str(color + row))
            curRowNum += 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
    finally:
        board.close_connection(sock)

    return 0

#updateInfoBoard.apply_async(args=[1, 2], expires=60)
