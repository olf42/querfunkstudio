#!/usr/bin/env python3

import cherrypy
import os.path

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *

class Querfunkadmin(object):

    def __init__(self, template_env):
        self.user_ = Querfunkuser()
        self.env = template_env

    @cherrypy.expose
    def index(self):
        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        return self.env.get_template('admin.html').render(username=user)


    @cherrypy.expose
    def items(self):
        items = self.backend_.get_items()
        return self.env.get_template('items.html').render(items=items)

    @cherrypy.expose
    def log(self):
        logs = self.backend_.get_log()
        for message in logs:
            message['type'] = LOG_DISPLAY[message['type']]
        return self.env.get_template('log.html').render(logs=logs)
