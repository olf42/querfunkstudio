#!/usr/bin/env python3

import cherrypy
import datetime
import sqlite3
import os.path
import random
from hashlib import sha512
from jinja2 import Environment, PackageLoader

DATABASE_DIR = "database"
DATABASE_FILE = "querfunkstudio_development.db"
DATABASE = os.path.join(os.path.dirname(__file__), DATABASE_DIR, DATABASE_FILE)
LOG_TYPE = {0:"info",
            1:"warning",
            2:"error"}
LOG_DISPLAY = {0:"success",
               1:"warning",
               2:"danger"}

ERROR_LOGIN_MSG = "Username not found, Password mismatch or user not active"
ERROR_SESSION_MSG = "No Username found in your Session. Please log in."
ERROR_USERCREATE_MSG = "User already exists! Choose a different Name and try again."
ERROR_PASSWORD_MSG = "Passwords don't match. Try again!"
ERROR_NOTSUPERUSER_MSG = "User is not superuser!"

SUCCESS_REGISTRATION_MSG = "Account created. Needs approval."

class Querfunkstudio(object):

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
            raise ValueError(ERROR_LOGIN_MSG)

        try:
            self.user_.check_username(username)
        except ValueError:
            cherrypy.session['username'] = None
            raise

        return username

    @cherrypy.expose
    def logout(self):
        if self.user_authenticated():
            cherrypy.session['username'] = None
        template = env.get_template('index.html')
        return template.render()


    @cherrypy.expose
    def start2(self, **kwargs):
        try:
            user = self.user_authenticated()
        except ValueError as e:
            return env.get_template('index.html').render(error=e)

        return env.get_template('start2.html').render(username=user)


    @cherrypy.expose
    def register(self, **kwargs):
        if len(kwargs)>0:
            try:
                self.process_request(kwargs)
            except ValueError as e:
                return env.get_template('index.html').render(error=e)
        return env.get_template('index.html').render(success=SUCCESS_REGISTRATION_MSG)

    @cherrypy.expose
    def start(self, **kwargs):
        if len(kwargs)>0:
            self.process_request(kwargs)
        try:
            user = self.user_authenticated()
        except ValueError as e:
            return env.get_template('index.html').render(error=e)

        return env.get_template('start.html').render(username=user)

    @cherrypy.expose
    def index(self, **kwargs):
        return env.get_template('index.html').render()

class Querfunkadmin(object):

    def __init__(self):
        pass

    def superuser_authenticated(self):
        try:
            username = cherrypy.session['username']
        except:
            return False
        if self.user_.check_superusername(username):
            return username
        else:
            return False


    @cherrypy.expose
    def index(self):
        user = self.user_authenticated()
        if not user:
            return env.get_template('index.html').render()
        else:

            return "Welcome to Trollotest Admin Interface"

    @cherrypy.expose
    def items(self):
        template = env.get_template('items.html')
        items = self.backend_.get_items()
        return template.render(items=items)

    @cherrypy.expose
    def log(self):
        template = env.get_template('log.html')
        logs = self.backend_.get_log()
        for message in logs:
            message['type'] = LOG_DISPLAY[message['type']]
        return template.render(logs=logs)


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

def encrypt_pw(pw):
        return sha512(pw.encode("utf-8")).hexdigest()


if __name__ == '__main__':

    env = Environment(loader=PackageLoader('querfunkstudio', 'templates'))
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Test Data
    if not os.path.isfile(DATABASE):
        users_ = Users()

        users_.create_db()

        users_.add_user(username="Thorsten",
                       password="Password",
                       active=0,
                       superuser=0)
        users_.add_user(username="olf",
                       password="Password",
                       active=1,
                       superuser=1)


    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8026,
        'server.thread_pool_max': 500,
        'server.thread_pool': 100,
        'log.screen': True
    })

    cherrypy.tree.mount(Querfunkstudio(), "/", {
            '/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': os.path.join(current_dir, 'public'),
                  'tools.sessions.on': True,
                  }
    })
    cherrypy.tree.mount(Querfunkadmin(), "/admin", {
            '/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': os.path.join(current_dir, 'public'),
                  'tools.sessions.on': True,
                  }
    })



    cherrypy.engine.start()
    cherrypy.engine.block()

