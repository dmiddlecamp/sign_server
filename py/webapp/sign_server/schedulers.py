'''
Created on Mar 21, 2012

@author: robert
'''
from celery.schedules import schedule
from time import time, localtime
import logging

logger = logging.getLogger(__name__)

class minute(schedule):
    def is_due(self, last_run_at):
        logger.warn("is_due returning true")
        return True, 60

    def __repr__(self):
        return "<minute>"