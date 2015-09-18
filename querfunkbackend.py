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
        return dict(zip(keys, [alias, self.schedule_id, querfunk.get_schedule()]))
        #return dict(zip(keys, [alias, self.schedule_id, querfunk.show_schedule()]))

    def get_schedules(self):
        schedules = self.backend_.get_schedules()
        if schedules:
            return schedules
        else:
            raise ValueError(ERROR_NOSCHEDULESFOUND_MSG)

    def generate_calendar(self, schedule_id):
        try:
            schedule = self.backend_.get_schedule(schedule_id)[0][0]
        except:
            raise ValueError(ERROR_SCHEDULENOTFOUND_MSG)
        querfunk = ScheduleView()
        querfunk.import_stationxml(schedule)
        shows = querfunk.get_shows()
        existing_shows = dict()
        added_shows = dict()
        for show_id, show_name in shows.items():
            try:
                self.backend_.add_show(show_id, show_name)
                added_shows[show_id] = show_name
            except:
                existing_shows[show_id] = show_name
        return added_shows, existing_shows, len(shows)

class Backend(object):

    def create_db(self):
        with sqlite3.connect(DATABASE) as c:
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          stationxml(id INTEGER PRIMARY KEY,
                                stationxml TEXT,
                                alias TEXT) ''')
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          shows(id INTEGER PRIMARY KEY,
                                name TEXT,
                                description TEXT) ''')
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          show_user(id INTEGER PRIMARY KEY,
                                    show_id INTEGER,
                                    username TEXT,
                                    FOREIGN KEY(show_id) REFERENCES shows(id),
                                    FOREIGN KEY(username) REFERENCES users(username)
                                    )''')

    def get_show(self, show_id):
        with sqlite3.connect(DATABASE) as c:
            result = c.execute(''' SELECT name, description
                                   FROM shows
                                   WHERE id=?''',
                                   (show_id,))
        try:
            return list(result.fetchall()[0])
        except:
            raise ValueError(ERROR_SHOWNOTFOUND_MSG)

    def add_show(self, show_id, name, description=''):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' INSERT INTO 
                              shows(id,
                                    name, 
                                    description) 
                              VALUES (?, ?, ?) ''',
                          (show_id,
                           name,
                           description))
            except ValueError:
                raise ValueError(ERROR_ADDSHOW_MSG)


    def add_stationxml(self, content, alias):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' INSERT INTO 
                              stationxml(alias, 
                                         stationxml) 
                              VALUES (?, ?) ''',
                          (alias,
                           content))
            except ValueError:
                raise ValueError(ERROR_STATIONXMLIMPORT_MSG)
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


