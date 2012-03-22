import socket
import sys
from struct import *
import array
from time import sleep
from django.http import HttpResponse
from numpy.oldnumeric.alter_code1 import char

__author__ = 'middleca'

BOARD_IP = '10.1.3.250'
BOARD_PORT = 25

maxContinuousWriteChars = 4 * (192)
_currentWriteCounter = 0


def get_connection():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)

    try:
        sock.connect((BOARD_IP, BOARD_PORT))
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(2)

    return sock

def close_connection(sock):
    sock.close()

def clear_board(sock):
    clear_panel(sock, 0)
    clear_panel(sock, 1)
    clear_panel(sock, 4)

    clear_panel(sock, 2)
    clear_panel(sock, 3)
    clear_panel(sock, 5)

def clear_panel(sock, panelNumber):
    calibrate(sock, panelNumber, True)

def calibrate(sock, display, clear=False):
    maxrows = 12
    maxcols = 80

    if not clear:
        write_to_board(sock, display, 0, 0, "DISPLAY " + str(display))

    for r in range(maxrows):
        m = ''
        for c in range(maxcols):
            if clear:
                m += ' '
            else:
                m += str(c)

        if not clear:
            write_to_board(sock, display, 0, 0, "DISPLAY " + str(display))
        write_to_board(sock, display, r, 0, m)


#0, 1, 4
#2, 3, 5
#
#0: 80, 12
#1: 80, 12
#2: 80, 12
#3: 80, 12
#4: 30, 12
#5: 30, 12
#

display_widths = {
    '0': { 'cols': 80, 'rows': 12, 'right': 1, 'below': 2 },
    '1': { 'cols': 80, 'rows': 12, 'right': 4, 'below': 3 },
    '4': { 'cols': 32, 'rows': 12, 'right': -1, 'below': 5 },

    '2': { 'cols': 80, 'rows': 12, 'right': 3, 'below': -1 },
    '3': { 'cols': 80, 'rows': 12, 'right': 5, 'below': -1 },
    '5': { 'cols': 32, 'rows': 12, 'right': -1, 'below': -1 }
}





def write_line_split(sock, display, row, col, line):
    if display < 0:
        return

    displayWidth = display_widths[str(display)]['cols']

    displayEnd = col + len(line)
    delta = displayEnd - displayWidth
    drawto = min(displayWidth, len(line))

    write_to_board(sock, display, row, col, line[0: drawto] )

    if delta >= 0:
        nextdisplay = display_widths[str(display)]['right']
        if nextdisplay >= 0:
            write_line_split(sock, nextdisplay, row, 0, line[drawto:])


def write_split(sock, display, row, col, lines):
    maxRows = display_widths[str(display)]['rows']

    for line in lines:
        if display < 0:
            break

        if row >= maxRows:
            display = display_widths[str(display)]['below']
            row = row - maxRows

        write_line_split(sock, display, row, col, line)
        row = row + 1
        pass
    pass

def write_file(filename):
    f = open(filename, 'r')
    sock = get_connection()
    write_split(sock, 0, 0, 0, f.readlines())
    close_connection(sock)

    #TODO: write inside a bounding box, wrapping rows as we go
    #try to detect and preserve colors
    # i.e. a color (29,30,31) should not count against available chars
    # i.e. a color should be detected and wrapped to the start of the next row

#def write_region(sock, display, row, col, msg, maxRow, maxCol):
#    maxRows = display_widths[str(display)]['rows']
#
#    for line in lines:
#        if display < 0:
#            break
#
#        if row >= maxRows:
#            display = display_widths[str(display)]['below']
#            row = row - maxRows
#
#        write_line_split(sock, display, row, col, line)
#        row = row + 1
#        pass
#    pass



def replace_colors(msg):
    msg = msg.replace("{#0}", chr(30))
    msg = msg.replace("{#1}", chr(31))
    msg = msg.replace("{#2}", chr(32))
    return msg





def write_to_board(sock, display, row, col, msg):
    global _currentWriteCounter

    #start byte 0x01
    #display + 0x32
    #row + 0x20
    #col + 0x20
    #message
    #null
    #0x04


    #str = 'a' + char(31) + str

    msg = replace_colors(msg)

    buffer = array.array('B', str(0) * (5+len(msg)))
    pack_into('BBBB'+ str(len(msg)) + 'sB', buffer, 0,
        0x01,
        display + 32,
        row + 0x20,
        col + 0x20,
        str(msg),
        #0x00,
        0x04
    )



    if _currentWriteCounter > maxContinuousWriteChars:
        _currentWriteCounter = 0
        sleep(0.250)

    _currentWriteCounter += len(buffer)


    #sock.send(buffer)
    sock.sendall(buffer)
    sleep(0.050)


    #if we draw too fast, we overwhelm the board.

    pass