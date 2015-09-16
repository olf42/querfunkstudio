#!/usr/bin/env python3

import cherrypy
import os.path

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *
from querfunkbackend import *

class Querfunkadmin(object):

    def __init__(self, template_env):
        self.user_ = Querfunkuser()
        self.backend_ = Querfunkbackend()
        self.env = template_env

    @cherrypy.expose
    def index(self):
        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)
        return self.env.get_template('admin.html').render(username=user)

    def process_import(self, kwargs):
        size = 0
        content = ''
        error = ''
        stationxml_file = kwargs['stationxml']
        alias = kwargs['alias']
        while True:
            data = stationxml_file.file.read(8192).decode('utf-8')
            if not data:
                break
            content += data
        try:
            return self.backend_.import_stationxml(content, alias)
        except ValueError as e:
            raise


    @cherrypy.expose(['import'])
    def import_schedule(self, **kwargs):
        success = ''
        error = ''

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        if len(kwargs)>0:
            try:
                success = self.process_import(kwargs)
            except ValueError as e:
                error=e
        return self.env.get_template('import.html').render(success=success,
                                                           error=error
                                                          )

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
