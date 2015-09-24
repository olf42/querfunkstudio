#!/usr/bin/env python3

import cherrypy
import sqlite3

from querfunkconfig import *
from querfunktools import *

class Querfunkuser(object):

    def __init__(self):
        self.user_ = Users()

    def process_request(self, kwargs):
        query = kwargs['query']

        # Login Processing
        if query == 'login':
            username = kwargs['username']
            password = kwargs['password']
            try:
                user_password = self.user_.get_password(username)[0][0]
            except:
                raise ValueError(ERROR_LOGIN_MSG)
            if user_password == encrypt_pw(password):
                cherrypy.session['username'] = username
            else:
                raise ValueError(ERROR_LOGIN_MSG)

        # Registration Processing
        elif query == 'register':
            username = kwargs['username']
            password = kwargs['password']
            password_repeat = kwargs['password_repeat']
            if password == password_repeat:
                try:
                    self.user_.add_user(username, password)
                except ValueError:
                    raise
            else:
                raise ValueError(ERROR_PASSWORD_MSG)

    def user_authenticated(self):
        try:
            username = cherrypy.session['username']
        except:
            raise ValueError(ERROR_SESSION_MSG)
        try:
            self.user_.check_username(username)
        except ValueError:
            cherrypy.session['username'] = None
            raise
        return username

    def superuser_authenticated(self):
        try:
            username = cherrypy.session['username']
        except:
            raise ValueError(ERROR_SESSION_MSG)
        try:
            self.user_.check_superusername(username)
        except ValueError:
            raise
        return username

class Users(object):

    def create_db(self):
        with sqlite3.connect(DATABASE) as c:
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          users(username TEXT PRIMARY KEY,
                                password TEXT,
                                active INTEGER,
                                superuser INTEGER) ''')

    def add_user(self, username, password, active=0, superuser=0):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' INSERT INTO 
                          users(username, 
                                password,
                                active,
                                superuser) 
                          VALUES (?, ?, ?, ?) ''',
                          (username,
                           encrypt_pw(password),
                           active,
                           superuser))
            except:
                raise ValueError(ERROR_USERCREATE_MSG)

    def check_username(self, username):
        result = None
        with sqlite3.connect(DATABASE) as c:
            user = c.execute(''' SELECT *
                          FROM users
                          WHERE username = ?
                          AND active=1''',
                          (username,))
        try:
            return user.fetchall()[0][1]
        except:
            raise ValueError(ERROR_LOGIN_MSG)


    def check_superusername(self, username):
        result = None
        with sqlite3.connect(DATABASE) as c:
            user = c.execute(''' SELECT *
                          FROM users
                          WHERE username = ?
                          AND active=1
                          AND superuser=1''',
                          (username,))
        try:
            return user.fetchall()[0][1]
        except:
            raise ValueError(ERROR_NOTSUPERUSER_MSG)

    def get_password(self, username):
        with sqlite3.connect(DATABASE) as c:
            user = c.execute(''' SELECT password
                          FROM users
                          WHERE username = ?''',
                          (username,))
        return user.fetchall()

    def get_user(self, username):
        result = None
        with sqlite3.connect(DATABASE) as c:
            user = c.execute(''' SELECT *
                                 FROM users
                                 WHERE username = ?''',
                                 (username,))
        try:
            return user.fetchall()[0]
        except:
            raise ValueError(ERROR_USERNOTFOUND_MSG)

    def get_users(self):
        with sqlite3.connect(DATABASE) as c:
            self.users = c.execute(''' SELECT username,password
                          FROM users''')
        return dict(self.users.fetchall())

    def get_superusers(self):
        with sqlite3.connect(DATABASE) as c:
            self.users = c.execute(''' SELECT username,password
                          FROM users WHERE superuser = 1''')
        return dict(self.users.fetchall())
