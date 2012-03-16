# Create your views here.
from time import time, localtime, strftime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from sign_server import board


def hello_world(request):
    return HttpResponse("Hello World")

def mini_board(request):
    maxCols = 192
    curCol = 0
    cols = []
    while curCol < maxCols:
        cols.append(curCol)
        curCol += 1

    maxRows = 24
    curRow = 0
    rows = []
    while curRow < maxRows:
        rows.append(curRow)
        curRow += 1

    return render_to_response('sign_server/miniBoard.html', {'cols': cols, 'rows': rows})


def board_test(request):
    msg = "Hello World"
    sock = board.get_connection()
    board.write_to_board(sock, 0, 0, 0, msg)
    board.close_connection(sock)

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

        board.close_connection(sock)

    except:
        board.close_connection(sock)

    return HttpResponse(content="Written")
