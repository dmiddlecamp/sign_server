__author__ = 'middleca'


class Position(object):
    panel = 0
    row = 0
    col = 0

    @staticmethod
    def empty():
        return Position()
