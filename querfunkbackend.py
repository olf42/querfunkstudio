#!/usr/bin/env python3

import cherrypy
import os.path

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *

class Querfunkbackend(object):

    def __init__(self):
        self.backend_ = Backend()

    def import_stationxml(self, content, alias):
        try:
            return self.backend_.add_stationxml(content, alias)
        except ValueError:
            raise

    def get_schedules(self):
        schedules = self.backend_.get_schedules()
        if schedules:
            return schedules
        else:
            raise ValueError(ERROR_NOSCHEDULESFOUND_MSG)

class Backend(object):

    def create_db(self):
        with sqlite3.connect(DATABASE) as c:
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          stationxml(id INTEGER PRIMARY KEY,
                                stationxml TEXT,
                                alias TEXT) ''')

    def add_stationxml(self, content, alias):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' INSERT INTO 
                          stationxml(alias, 
                                stationxml) 
                          VALUES (?, ?) ''',
                          (alias,
                           content))
            except ValueError as e:
                raise ValueError(ERROR_STATIONXMLIMPORT_MSG + e)
        return SUCCESS_STATIONXMLIMPORT_MSG.format(alias)

    def get_schedules(self):
        result = []
        keys = ['id', 'alias']
        with sqlite3.connect(DATABASE) as c:
            self.schedules = c.execute(''' SELECT id,alias
                                                  FROM stationxml''')
            for item in self.schedules.fetchall():
                result.append(dict(zip(keys, list(item))))
        return result


