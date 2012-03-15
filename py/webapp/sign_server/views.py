# Create your views here.
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
    sock = board.get_connection()

    board.calibrate(sock, 0)
    board.calibrate(sock, 1)
    board.calibrate(sock, 2)
    board.calibrate(sock, 3)
    board.calibrate(sock, 4)
    board.calibrate(sock, 5)
    board.calibrate(sock, 6)


    board.close_connection(sock)

    return HttpResponse(content="Calibrated")

def file_test(request):
    board.write_file('/projects/sign_server/hello_board.txt')

    return HttpResponse(content="Displayed Test")

