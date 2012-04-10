from struct import *
from time import sleep
import array
import socket
import sys

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



def write_line_split(sock, display, row, col, line, maxCol=-1):
    """
    A non-recursive line writer that spans panels
    """

    if display < 0:
        return

    charsToWrite = len(line)

    #check to see if we have more than we can write
    leftoversStr = ''
    if maxCol > 0 and (charsToWrite + col) > maxCol:
        longestWriteAllowed = (maxCol-col)
        leftoversStr = line[longestWriteAllowed:]
        line = line[0:longestWriteAllowed]
        charsToWrite = len(line)

    lastColor = -1

    while charsToWrite > 0:
        displayWidth = display_widths[str(display)]['cols']

        if col > displayWidth:
            #move to the next board
            col -= displayWidth
            nextdisplay = display_widths[str(display)]['right']
            if nextdisplay < 0:
                return line + leftoversStr     #we don't have anywhere to go, bail

            display = nextdisplay

        lastCharToDisplay = min(displayWidth - col, len(line))
        write_to_board(sock, display, row, col, line[0: lastCharToDisplay] )

        lastColor = findLastColor(line[0: lastCharToDisplay])

        line = line[lastCharToDisplay:]

        #something like this, where what we write doesn't have to perfectly line up, or something...
        #if lastColor > 0:
        #    line = chr(lastColor) + line

        charsToWrite = len(line) - countControlCodes(line)



    return leftoversStr


def findLastColor(msg):
    colors = [ 29, 30, 31 ]
    lastIdx = -1
    lastColor = -1
    for c in colors:
        colorChar = chr(c)
        idx = str(msg).rfind(colorChar)
        if idx > lastIdx:
            lastColor = colorChar

    return lastColor

def countControlCodes(msg):
    controlCodes = [ 29, 30, 31 ]

    #please to be making efficient
    count = 0
    for c in controlCodes:
        c = chr(c)
        count += msg.count(c)

    return count


#
#
#
#
#
#
#    #how wide is this particular display? (relative length, 0-80, 0-32)
#
#
#    #how many columns does our message cover?
#    messageEnd = col + len(line)
#
#    #don't let our message pass our imaginary boundary
#    wrappedStr = ''
#    if maxCol > 0 and messageEnd > maxCol:
#        longestWriteAllowed = (maxCol-col)
#        wrappedStr = line[longestWriteAllowed:]
#        line = line[0:longestWriteAllowed]
#        #messageEnd = max(maxCol, messageEnd)
#
#    #do we need more than one write operation?
#    delta = messageEnd - displayWidth
#
#
#
#
#    #how many characters of this message, can we show on this display?
#    # e.g. if we start writing at column 5, and there are 80 columns, then we can write 75 chars, or len(line), whichever comes first
#    lastCharToDisplay = min(displayWidth - col, len(line))
#
#    while lastCharToDisplay < 0:
#        #scroll right until we can write
#        display = display_widths[str(display)]['right']
#        if nextdisplay >= 0:
#            displayWidth = display_widths[display]['cols']
#            lastCharToDisplay = min(displayWidth - col, len(line))
#
#
#    #write what we can to this display
#    write_to_board(sock, display, row, col, line[0: lastCharToDisplay] )
#
#
#    if delta >= 0:
#        #keep writing the rest of this message at the start of the next board to the right
#        nextdisplay = display_widths[str(display)]['right']
#        if nextdisplay >= 0:
#            return write_line_split(sock,
#
#                nextdisplay, row, 0,
#                line[lastCharToDisplay:], maxCol=maxCol)
#        else:
#            #we're probably line / word wrapping, so return our leftovers
#            return line[lastCharToDisplay:] + wrappedStr
#    else:
#        #we're done
#        return wrappedStr


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

#def write_to_board(sock, display, beginRow, beginCol, endRow, endCol, payload):
    

def write_file(filename):
    f = open(filename, 'r')
    sock = get_connection()
    write_split(sock, 0, 0, 0, f.readlines())
    close_connection(sock)

    #TODO: write inside a bounding box, wrapping rows as we go
    #try to detect and preserve colors
    # i.e. a color (29,30,31) should not count against available chars
    # i.e. a color should be detected and wrapped to the start of the next row


def write_region_wrap(sock, display, row, col, msg, maxRow, maxCol):
    """
    Takes a very long 'msg' and wraps it in the provided bounds
    """

    if row < 0:
        row = 0
    if col < 0:
        col = 0
    if maxRow < 0 or maxRow > 24:
        maxRow = 24
    if maxCol < 0 or maxCol > 192:
        maxCol = 192

    remainingMsg = write_line_split(sock, display, row, col, msg, maxCol=maxCol)
    while len(remainingMsg) > 0 and row < maxRow:
        row += 1
        remainingMsg = write_line_split(sock, display, row, col, remainingMsg, maxCol=maxCol)

    pass





    #maxRows = display_widths[str(display)]['rows']

#    #for line in lines:
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
#    #pass



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