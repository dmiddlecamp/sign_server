'''
Created on Apr 18, 2012

@author: robert
'''
from sign_server import board

def clear_board(row, **kwargs):
    sock = None
    try:
#        sock = board.get_connection()
        board.clear_panel(sock, 0)
        board.clear_panel(sock, 1)
        board.close_connection(sock)
    except:
        board.close_connection(sock)
        return False
    return True

def write_to_board(row, col, msg, **kwargs):
    sock = None
    try:
#        sock = board.get_connection()
        board.write_split(sock, 0, row, col, [ msg ])
        board.close_connection(sock)
    except:
        board.close_connection(sock)
#        print "Unexpected error:", sys.exc_info()[0]
        return False
    return True