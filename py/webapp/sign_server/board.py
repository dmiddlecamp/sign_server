from struct import *
from time import sleep
import array
import re
import socket
import sys

__author__ = 'middleca'

BOARD_IP = '10.1.3.250'
BOARD_PORT = 25

BOARD_PORT_TOP = 26
BOARD_PORT_BOTTOM = 27


maxContinuousWriteChars = 4 * 192
_currentWriteCounter = 0

display_sockets = {
    'Empty': None
}

display_widths = {
    '0': { 'cols': 80, 'rows': 12, 'right': 1, 'below': 2, 'port': BOARD_PORT_TOP },
    '1': { 'cols': 80, 'rows': 12, 'right': 4, 'below': 3, 'port': BOARD_PORT_TOP },
    '4': { 'cols': 32, 'rows': 12, 'right': -1, 'below': 5, 'port': BOARD_PORT_TOP },

    '2': { 'cols': 80, 'rows': 12, 'right': 3, 'below': -1, 'port': BOARD_PORT_BOTTOM },
    '3': { 'cols': 80, 'rows': 12, 'right': 5, 'below': -1, 'port': BOARD_PORT_BOTTOM },
    '5': { 'cols': 32, 'rows': 12, 'right': -1, 'below': -1, 'port': BOARD_PORT_BOTTOM }
}


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

def get_connection_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(1)

    try:
        sock.connect((BOARD_IP, port))
    except socket.error, msg:
        sys.stderr.write("[ERROR] %s\n" % msg[1])
        sys.exit(2)

    return sock


def close_connection(sock):
    global display_sockets

    if sock is not None:
        sock.close()
    else:
        #for now, lets just close everything
        for key in display_sockets.keys():
            if display_sockets[key] is not None:
                display_sockets[key].close()

        display_sockets = { 'Empty': None }


    pass

def reset_connection_split(display, row, col):
    port = None
    global display_sockets
    global display_widths

    if display is not None:
        port = display_widths[str(display)]['port']

    if port is None:
        #TODO: figure out where we are... but I think we shouldn't get here.
        pass

    key = str(port)
    display_sockets[key] = get_connection_port(port)
    return display_sockets[key]


def get_connection_split(display, row, col):
    '''
    This function should grab or create a cached socket, not sure when to close it!
    '''
    port = None
    global display_sockets
    global display_widths

    if display is not None:
        port = display_widths[str(display)]['port']

    if port is None:
        #TODO: figure out where we are... but I think we shouldn't get here.
        pass

    key = str(port)

    if display_sockets.has_key(key) is False:
        display_sockets[key] = get_connection_port(port)

    return display_sockets[key]
    pass


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

        lastCharToDisplay = min(displayWidth - col, len(line))
        write_to_board(sock, display, row, col, line[0: lastCharToDisplay] )

        lastColor = findLastColor(line[0: lastCharToDisplay])

        line = line[lastCharToDisplay:]

        if lastCharToDisplay == displayWidth:
             #move to the next board
            col = 0
            nextdisplay = display_widths[str(display)]['right']
            if nextdisplay < 0:
                return line + leftoversStr     #we don't have anywhere to go, bail
            display = nextdisplay


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



def find_display_for(row, col, fix_coords=False):
    '''Finds the correct display for a given row/column'''

    global display_widths

    r = 0
    c = 0

    for display_key in display_widths:
        info = display_widths[display_key]

        if (row >= r) and (row < (r + info['rows'])):
            if (col >= c) and (col < (c + info['cols'])):
                if fix_coords:
                    row = row - r
                    col = col - c
                    return display_key, row, col,
                else:
                    return display_key

        r = r + info['rows']
        c = c + info['cols']

        pass #end of loops

    return 0


def write_split(sock, display, row, col, lines):
    if display < 0:
        display, row, col = find_display_for(row, col, fix_coords=True)

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
    write_split(None, 0, 0, 0, f.readlines())
    #close_connection(sock)

    #TODO: write inside a bounding box, wrapping rows as we go
    #try to detect and preserve colors
    # i.e. a color (29,30,31) should not count against available chars
    # i.e. a color should be detected and wrapped to the start of the next row


def write_file_coords(filename, row, col):
    f = open(filename, 'r')
    write_split(None, -1, row, col, f.readlines())

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

def remap_chars(msg):
    msg = re.sub('\[', '\(', msg)
    msg = re.sub('\\\\', '\/', msg)
    msg = re.sub('\]', '\)', msg)
    msg = re.sub('\^', '-', msg)
    msg = re.sub('_', '-', msg)
    msg = re.sub('`', '\'', msg)
    msg = re.sub('{', '\(', msg)
    msg = re.sub('\|', '1', msg)
    msg = re.sub('}', '\)', msg)
    msg = re.sub('~', '-', msg)
    return msg


def write_to_board(sock, display, row, col, msg):
    global _currentWriteCounter

    # what we're sending...
    #
    #start byte 0x01
    #display + 0x32
    #row + 0x20
    #col + 0x20
    #message
    #null
    #0x04

    #str = 'a' + char(31) + str

    msg = replace_colors(msg)
    msg = remap_chars(msg)

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

    if sock is None:
        sock = get_connection_split(display, row, col)

    #sock.send(buffer)
    try:
        sock.sendall(buffer)
    except Exception, e:
        # we probably lost the connection...
        sock = reset_connection_split(display, row, col)
        sock.sendall(buffer)


    #if we draw too fast, we overwhelm the board.
    sleep(0.050)

    pass