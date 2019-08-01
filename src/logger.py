#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
Photomaton logger path
'''
import os
import json
import filelock

SHAREDOBJECTPATH = '/dev/shm/shared.json'#sharedmemory no present avant python 3.8

LOG_INFO = 0
LOG_ERROR = 1

LOGDICT = {
    LOG_INFO: 'LOG_INFO',
    LOG_ERROR: 'LOG_ERROR'
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
        with filelock.FileLock(SHAREDOBJECTPATH):
            try:
                sharedobject = json.loads(open(SHAREDOBJECTPATH).read())
            except(FileNotFoundError, json.decoder.JSONDecodeError):
                sharedobject = {}
            if printerstatus: sharedobject['printerstatus'] = printerstatus
            if addprintercount:
                if sharedobject['printercount']: sharedobject['printercount'] += addprintercount
                if sharedobject['printercount']: sharedobject['printercount'] = addprintercount
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
