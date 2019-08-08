#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
Admin and monitoring server
'''
import os
import json
import hashlib
import time
import textile
import threading
import functools
import binascii
import argparse
import flask
import flask_sse
import flask_sslify
import psutil

application = flask.Flask(__name__)
application.config['MAX_CONTENT_LENGTH'] = 9999999
application.secret_key = os.urandom(512)
application.config["REDIS_URL"] = "redis://localhost:6379"
application.register_blueprint(flask_sse.sse, url_prefix='/stream')
flask_sslify.SSLify(application, permanent=True)

CURRPATH = os.path.dirname(os.path.realpath(__file__))
NOAUTH = False
SHAREDOBJECTPATH = '/dev/shm/shared.json'

class backgroundexec(threading.Thread):
    '''
    Background thread gère le redis
    '''
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        with application.app_context():
            while True:
                time.sleep(5)
                paramlist = ['printerstatus', 'printercount', 'internalerror']
                try:
                    shared_data = json.loads(open(SHAREDOBJECTPATH).read())
                    for i in paramlist:
                        try:
                            flask_sse.sse.publish({'message': shared_data[i]}, type=i)
                        except KeyError:
                            flask_sse.sse.publish({'message': 'UNKNOWN'}, type=i)
                except (FileNotFoundError, json.decoder.JSONDecodeError):
                    for i in paramlist:
                        flask_sse.sse.publish({'message': 'UNKNOWN'}, type=i)
                flask_sse.sse.publish({'message': '{} %'.format(psutil.cpu_percent())},
                                      type='cpupercent')
                flask_sse.sse.publish({'message': '{} %'.format(
                    psutil.sensors_temperatures()[list(psutil.sensors_temperatures())[0]][0].current)},
                                      type='cputemp')
                flask_sse.sse.publish({'message': '{} %'.format(psutil.virtual_memory().percent)},
                                      type='mempercent')
                try:
                    lastlog = open(os.path.join(CURRPATH, '..', 'log', 'logs.txt'
                                               )).readlines()[-10:]
                    flask_sse.sse.publish({'message': '{}'.format(''.join('{}<br/>'.format(x) for x in lastlog))},
                                          type='lastlog')
                except: pass

def require_admin(func):
    '''
    Demande de credentials admin
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global NOAUTH
        if NOAUTH:
            flask.session['username'] = 'admin'
            return func(*args, **kwargs)
        currpath = os.path.dirname(os.path.realpath(__file__))
        logins = list(json.loads(open(os.path.join(currpath, 'password.json')).read()))
        if 'username' in flask.session and flask.session['username'] == 'admin':
            return func(*args, **kwargs)
        if 'username' in flask.session and flask.session['username'] in logins:
            return flask.abort(500)
        return flask.redirect('/login')
    return wrapper

@application.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Password login
    '''
    credentials = json.loads(open(os.path.join(CURRPATH, 'password.json')).read())
    if flask.request.method == 'POST':
        user = flask.request.form['username']
        if user in credentials:
            salt = bytes(credentials[user]['salt'], 'UTF-8')
            userhash = credentials[user]['hash']
            dbhash = str(binascii.hexlify(hashlib.pbkdf2_hmac('sha512',
                                                              bytes(flask.request.form['password'],
                                                                    'UTF-8'), salt, 1000000)),
                         'UTF-8')
            print(dbhash, userhash)
            if dbhash == userhash:
                flask.session['username'] = user
                print('OK')
                return flask.redirect('/')
    return flask.render_template('auth.html', status=None)


@application.route('/logout', methods=['GET', 'POST'])
@require_admin
def logout():
    '''
    Disconnect Session
    '''
    if 'username' in flask.session:
        flask.session['username'] = None
    return flask.redirect('/')

@application.route('/api', methods=['GET', 'POST'])
def api():
    lastlog = open(os.path.join(CURRPATH, '..', 'log', 'logs.txt')).readlines()[-10:]
    retval = {
             'shared_data': json.loads(open(SHAREDOBJECTPATH).read()),
             'machine': {
                'cpu_percent': psutil.cpu_percent(),
                'cputemp': psutil.sensors_temperatures()[list(psutil.sensors_temperatures())[0]][0].current,
                'mempercent': psutil.virtual_memory().percent
             },
                'logs': lastlog[::-1]
             }
    return '<html><header><meta http-equiv="refresh" content="5"></header><body>{}</body></html>'.format(textile.textile(json.dumps(retval, indent=4)).replace('\n', '<br/>\n').replace(' ', '&nbsp'))

@application.route('/', methods=['GET', 'POST'])
def index():
    '''
    Affiche le menu
    '''
    thread_1 = backgroundexec()
    thread_1.start()
    return flask.render_template('mainmenu.html', status=None)

def parse_command_line():
    '''
    Parse les arguments
    '''
    parser = argparse.ArgumentParser(description='Launch server (Flask)')
    parser.add_argument('--host', help='Host Adress to listen to', default="0.0.0.0")
    parser.add_argument('--port', help='Port Adress to listen to', default=4443)
    parser.add_argument('--nossl', help="Service doesn't use SSL", action="store_true")
    parser.add_argument('--noauth', help="Disable auth", action="store_true")
    parser.add_argument('--cert', help='Specific certificate to use for SSL',
                        default=os.path.join(CURRPATH, "cert.pem"))
    parser.add_argument('--key',
                        help='Specific key to use for SSL',
                        default=os.path.join(CURRPATH, "key.pem"))
    return parser.parse_args()

if __name__ == '__main__':
    ARGS = parse_command_line()
    NOAUTH = ARGS.noauth
    if ARGS.nossl:
        application.run(threaded=True, host=ARGS.host, port=ARGS.port, debug=False)
    else:
        SSLCONTEXT = (ARGS.cert, ARGS.key)
        application.run(threaded=True, host=ARGS.host, port=ARGS.port, debug=False, ssl_context=SSLCONTEXT)
