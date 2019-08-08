#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
Photomaton logger path
'''
import os
import json
import filelock

SHAREDOBJECTPATH = '/dev/shm/shared.json'#sharedmemory no present avant python 3.8

LOG_DEBUG = -1
LOG_INFO = 0
LOG_ERROR = 1


LOGDICT = {
    LOG_INFO: 'LOG_INFO',
    LOG_ERROR: 'LOG_ERROR',
    LOG_DEBUG: 'LOG_DEBUG'
}

CURRDIR = os.path.abspath(os.path.dirname(__file__))

class logger:
    '''
    Logger class
    '''
    @staticmethod
    def logStatus(printerstatus=None, addprintercount=None, internalerror=None):
        '''
        Send status to the server
        '''
        try:
            sharedobject = json.loads(open(SHAREDOBJECTPATH).read())
        except(FileNotFoundError, json.decoder.JSONDecodeError):
            sharedobject = {}
        with filelock.FileLock(SHAREDOBJECTPATH):
            if printerstatus: sharedobject['printerstatus'] = printerstatus
            if addprintercount:
                if 'printercount' in list(sharedobject): sharedobject['printercount'] += addprintercount
                else: sharedobject['printercount'] = addprintercount
            if internalerror: sharedobject['internalerror'] = internalerror
            open(SHAREDOBJECTPATH, 'w').write(json.dumps(sharedobject, indent=4))

    @staticmethod
    def logEvent(loglevel, event):
        '''
        log locally an event
        '''
        if loglevel == LOG_ERROR: logger.logStatus(internalerror=event)
        open(os.path.join(CURRDIR,
                          '..',
                          'log',
                          'logs.txt'), 'a+').write('{} {}\n'.format(LOGDICT[loglevel], event))
