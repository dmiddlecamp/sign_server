__author__ = 'middleca'


class Controller(object):
    widget_list = []


    def tick(self):
        """
        figures out what needs to run, allows widgets to be registered, and write to the board
        """

