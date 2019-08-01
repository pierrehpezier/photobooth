#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
Fichier de gestion de mot de passe
'''
import os
import hashlib
import getpass
import binascii
import json

def create_creds(login):
    '''
    Changement de mot de passe du serveur
    '''
    while True:
        password = getpass.getpass(prompt='Password: ', stream=None)
        if password == getpass.getpass(prompt='Repeat password: ', stream=None):
            break
        print('''password don't match''')
    salt = bytes(binascii.hexlify(os.urandom(56)))
    return {login: {'salt': str(salt, 'UTF-8'),
                    'hash': str(binascii.hexlify(hashlib.pbkdf2_hmac('sha512',
                                                                     bytes(password, 'UTF-8'),
                                                                     salt, 1000000)), 'UTF-8')}}

if __name__ == '__main__':
    open('password.json', 'w').write(json.dumps(create_creds('admin'), indent=4))
