from time import time, localtime, strftime

__author__ = 'middleca'


class Widget(object):
    #schedule = None
    #Envelope
    env = None
    buffered_frame = ''

    #TODO: wipe_envelope option, to send to the board writer, so it wipes any unused space in its envelope if requested


    def render(self):
        newFrame = self.updateBuffer()
        if newFrame == self.buffered_frame:
            return None

        self.buffered_frame = newFrame
        return newFrame



    def updateBuffer(self):
        """
        This is just an example, obv.
        """
        secs = time()
        return strftime("%a, %d %b %Y %H:%M", localtime(secs) )

