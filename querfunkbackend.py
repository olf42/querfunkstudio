#!/usr/bin/env python3

import cherrypy
import os.path

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *
from querfunkstationxml import *

class Querfunkbackend(object):

    def __init__(self):
        self.backend_ = Backend()

    def import_stationxml(self, content, alias):
        try:
            return self.backend_.add_stationxml(content, alias)
        except ValueError:
            raise

    def get_schedule(self, kwargs):
        keys = ['alias', 'id', 'content']
        try:
            self.schedule_id = kwargs['id']
        except:
            raise ValueError(ERROR_SCHEDULENOTFOUND_MSG)

        try:
            schedule = self.backend_.get_schedule(self.schedule_id)
            alias = schedule[0][1]
            schedule = schedule[0][0]
        except:
            raise ValueError(ERROR_SCHEDULENOTFOUND_MSG)

        querfunk = ScheduleView()
        querfunk.import_stationxml(schedule)
        return dict(zip(keys, [alias, self.schedule_id, querfunk.show_schedule()]))

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

    def get_schedule(self, schedule_id):
        with sqlite3.connect(DATABASE) as c:
            result = c.execute(''' SELECT stationxml, alias
                                   FROM stationxml
                                   WHERE id=?''',
                                   (schedule_id,))
        return result.fetchall()

    def get_schedules(self):
        result = []
        keys = ['id', 'alias']
        with sqlite3.connect(DATABASE) as c:
            self.schedules = c.execute(''' SELECT id,alias
                                                  FROM stationxml''')
            for item in self.schedules.fetchall():
                result.append(dict(zip(keys, list(item))))
        return result


