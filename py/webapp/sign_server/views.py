# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response


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