#!/usr/bin/env python3

import cherrypy
import os.path

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *
from querfunkbackend import *

class Querfunkstudio(object):

    def __init__(self, template_env):
        self.user_ = Querfunkuser()
        self.backend_ = Querfunkbackend()
        self.env = template_env

    @cherrypy.expose
    def logout(self):
        try:
            self.user_.user_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)
        cherrypy.session['username'] = None

        return self.env.get_template('index.html').render()


    @cherrypy.expose
    def start2(self,):
        try:
            user = self.user_.user_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        return self.env.get_template('start2.html').render(username=user)


    @cherrypy.expose
    def register(self, **kwargs):
        if len(kwargs)>0:
            try:
                self.user_.process_request(kwargs)
            except ValueError as e:
                return self.env.get_template('index.html').render(error=e)
        return self.env.get_template('index.html').render(success=SUCCESS_REGISTRATION_MSG)

    @cherrypy.expose
    def start(self, **kwargs):
        if len(kwargs)>0:
            try:
                self.user_.process_request(kwargs)
            except ValueError as e:
                return self.env.get_template('index.html').render(error=e)


        try:
            user = self.user_.user_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        superuser = False

        try:
            superuser = self.user_.superuser_authenticated()
        except:
            pass

        try:
            shows = self.backend_.get_user_shows(user)
        except:
            pass

        return self.env.get_template('start.html').render(username=user,
                                                          superuser=superuser,
                                                          shows=shows)

    @cherrypy.expose
    def index(self, **kwargs):
        return self.env.get_template('index.html').render()
