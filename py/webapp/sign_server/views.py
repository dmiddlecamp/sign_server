# Create your views here.
from dircache import annotate
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from sign_server import board, twitter, weather, announcements, board_updater
from sign_server.announcements import UpdateAnnouncementsForm
from sign_server.board_updater import updateTwitterBoard, updateNetworkStatus
from sign_server.models import Announcement
from time import time, localtime, strftime
import sys

def home(request):
    return render_to_response('sign_server/home.html')

def hello_world(request):
    return HttpResponse("Hello World")

def mini_board(request):
#    maxCols = 192
    maxCols = 96
    curCol = 0
    cols = []
    while curCol < maxCols:
        cols.append(curCol)
        curCol += 1

#    maxRows = 24
    maxRows = 12
    curRow = 0
    rows = []
    while curRow < maxRows:
        rows.append(curRow)
        curRow += 1

    return render_to_response('sign_server/miniBoard.html', {'cols': cols, 'rows': rows})


def board_test(request):

    sock = board.get_connection()
    #board.write_to_board(sock, 0, 5, 15, "You have no chance to survive")
    #board.write_to_board(sock, 0, 6, 20, "Make your time")

#    board.write_to_board(sock, 0, 7, 20, "Boom zig")
#    board.write_to_board(sock, 0, 8, 30, "Boom zig")
#    board.write_to_board(sock, 0, 9, 40, "Boom zig")
#    board.write_to_board(sock, 0, 10, 50, "Boom zig")

    #board.write_split(sock, 0, 2, 30, [ "That's gotta be rough", ])
    #board.write_split(sock, 0, 3, 40, [ chr(30) + "Sorry, technical difficulties", ])

    #board.write_split(sock, 1, 0, 10, chr(30) + "Vertical Text!")

    #chr(30) +
    board.write_split(sock, 1, 0, 0, [ "Demerit Board:                                         ", ])

    demerits = [
        ("@DonohuePatrickE", 6,),
        ("@IdeaFood", 1,),
        ("@donmball", 0,),
        ("       ", ' ',),
    ]
    rowIdx = 1
    for d in demerits:
        board.write_split(sock, 1, rowIdx, 0, [  "                                       ", ])
        board.write_split(sock, 1, rowIdx, 2, [  chr(31) + d[0], ])

#        colorStr = ''
#        if d[1] > 1:
#            colorStr = chr(31)
#        if d[1] >= 3:
#            colorStr = chr(30)

        board.write_split(sock, 1, rowIdx, 25, [  chr(30) + str(d[1]) + "             ", ])
        rowIdx += 1




    board.close_connection(sock)

    #updateTwitterBoard(1, 2)

    return HttpResponse(content="Okay")

def calibrate_displays(request):
    try:
        sock = board.get_connection()

        board.calibrate(sock, 0)
        board.calibrate(sock, 1)
        board.calibrate(sock, 2)
        board.calibrate(sock, 3)
        board.calibrate(sock, 4)
        board.calibrate(sock, 5)
        #board.calibrate(sock, 6)

        board.close_connection(sock)

    except:
        board.close_connection(sock)

    return HttpResponse(content="Calibrated")

def clear_board(request):
    try:
        sock = board.get_connection()

        board.clear_board(sock)

        board.close_connection(sock)

    except:
        board.close_connection(sock)

    return HttpResponse(content="Cleared")


def file_test(request):
    board.write_file('/projects/sign_server/happy_friday.txt')

    return HttpResponse(content="Displayed Test")


def time_stamp(request):

    secs = time()
    lastTime = strftime("%a, %d %b %Y %H:%M:%S", localtime(secs) )
    timeLen = len('Thu, 28 Jun 2001 14:17:15')

    try:
        sock = board.get_connection()

        #TODO: calculate when clearing is necessary (e.g. when formatted string length changes from prev)
        #board.write_to_board(sock, 4, 0, 0, "                                ")
        board.write_to_board(sock, 4, 0, 0, lastTime)

        msg = "Hi Teke"
        board.write_to_board(sock, 5, 11, 32 - len(msg), msg)

        msg = "Hi ROBERT!"
        board.write_to_board(sock, 5, 9, 32 - len(msg), msg)

        board.close_connection(sock)

    except:
        board.close_connection(sock)

    return HttpResponse(content="Written")



def rawInterface(request, row, col, msg):
    row = int(row)
    col = int(col)
    try:
        sock = board.get_connection()

        board.write_split(sock, 0, row, col, [ msg ])
        #board.write_to_board(sock, 0, row, col, msg)

        board.close_connection(sock)

    except:
        board.close_connection(sock)

    return HttpResponse(content="Wrote " + msg)


def rawRegionInterface(request, row, rowlimit, col, collimit, msg):

    row = int(row)
    rowlimit = int(rowlimit)
    col = int(col)
    collimit = int(collimit)

    responseMsg = "Running..."

    try:
        sock = board.get_connection()


        board.clear_panel(sock, 1)

        board.write_region_wrap(sock, 0, row, col, msg, rowlimit, collimit)
        responseMsg = "Wrote " + msg

        board.close_connection(sock)


    except:
        responseMsg = "Err"
    finally:
        board.close_connection(sock)

    return HttpResponse(content=responseMsg)



def twitter_panel(request):
    try:
        sock = board.get_connection()
#        tb = twitter_board.TwitterBoard()
#        board.clear_panel(sock, 2)
        board.write_to_board(sock, 2, 0, 0, "*************** Tweets ********************************************************")
        curRowNum = 1
        for row in twitter.Twitter().getNewTweets(11, 79):
            board.write_to_board(sock, 2, curRowNum, 0, str(row + ' '))
            curRowNum += 1
    except:
        print "Unexpected error:", sys.exc_info()[0]
    finally:
        board.close_connection(sock)

    return HttpResponse(content="Twitter Board Updated")


def info_panel(request):
    try:
        sock = board.get_connection()
#        tb = twitter_board.TwitterBoard()
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

    return HttpResponse(content="Info Board Updated")

def network_status(request):
    updateNetworkStatus()

    return HttpResponse(content="Network Status Updated")


def view_announcements(request):
    announcements = Announcement.objects.all()
    render_to_response('robertsTest/messages.html', {'announcements': announcements})


def update_announcements(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UpdateAnnouncementsForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            announcement = Announcement()
            announcement.announcement_text = form.cleaned_data['text']
            announcement.created_date = time()
            announcement.save()
            return HttpResponse(content="Thank you")
        else:
            return HttpResponse(content="This did not work at all!")

def announcements_panel(request):
    board_updater.updateAnnouncementBoard(1, 2)
    return HttpResponse(content="Announcement Board Updated")
