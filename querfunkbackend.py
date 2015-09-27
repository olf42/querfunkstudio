#!/usr/bin/env python3

import cherrypy
import os.path

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *
from querfunkstationxml import *
from querfunklog import *

class Querfunkbackend(object):

    def __init__(self):
        self.log_ = Log()
        self.backend_ = Backend()
        self.users_ = Users()

    def import_stationxml(self, content, alias):
        try:
            return self.backend_.add_stationxml(content, alias)
        except ValueError:
            raise

    def get_schedule(self, kwargs):
        keys = ['alias', 'id', 'content', 'dates']
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
        return dict(zip(keys, [alias,
                               self.schedule_id,
                               querfunk.get_schedule(),
                               querfunk.get_dates()
                              ]
                        )
                    )

    def get_schedules(self):
        schedules = self.backend_.get_schedules()
        if schedules:
            return schedules
        else:
            raise ValueError(ERROR_NOSCHEDULESFOUND_MSG)

    def generate_calendar(self, schedule_id):

        # First, we check, if this schedule was already added
        if self.backend_.calendar_exists(schedule_id):
            raise ValueError(ERROR_CALENDAREXISTS_MSG.format(schedule_id))

        try:
            schedule = self.backend_.get_schedule(schedule_id)[0][0]
        except:
            raise ValueError(ERROR_SCHEDULENOTFOUND_MSG)
        querfunk = ScheduleView()
        querfunk.import_stationxml(schedule)

        #Search for shows not yet in the db and add them
        shows = querfunk.get_shows()
        existing_shows = dict()
        added_shows = dict()
        for show_id, show_name in shows.items():
            try:
                self.backend_.add_show(show_id, show_name)
                added_shows[show_id] = show_name
            except:
                existing_shows[show_id] = show_name

        #Create the calendar

        start, end = querfunk.get_dates_obj()

        #Check if enddate is after startdate
        if (end-start).days<0:
            raise ValueError(ERROR_STATIONXMLDATES_MSG)

        today = start
        while True:
            week = int(((today.day-1)/7)+1)
            weekday = today.weekday()+1

            year = today.year
            month = today.month
            day = today.day

            for show in querfunk.get_day(week, weekday).items():
                #check if there is a show for specific time
                if show[1]:
                    hour = int(show[0])
                    live = LIVE_REPEAT[show[1]['live']]
                    show_id = show[1]['id']
                    length = show[1]['length']

                    try:
                        self.backend_.add_episode((year, month, day, hour, length, live, show_id, schedule_id))
                    except:
                        episode_string = today.strftime("%Y-%m-%d")+" "+str(hour)+" "+str(show_id)
                        raise ValueError(ERROR_ADDEPISODE_MSG.format(episode_string))

            #increment and check
            today+=datetime.timedelta(1)
            if (today-end).days>0:
                break

        self.log_.write_log(LOG_ADDEDCALENDAR_MSG.format(schedule_id))

        return added_shows, existing_shows, len(shows)

    def get_shows(self):
        shows = self.backend_.get_shows()
        if shows:
            return shows
        else:
            raise ValueError(ERROR_NOSHOWSFOUND_MSG)

    def get_users(self):
        users = self.users_.get_users()
        if users:
            return users
        else:
            raise ValueError(ERROR_NOUSERSFOUND_MSG)

    def get_superusers(self):
        users = self.users_.get_superusers()
        if users:
            return users
        else:
            raise ValueError(ERROR_NOUSERSFOUND_MSG)

    def get_userdata(self, username):
        userkeys = ['name', 'password', 'active', 'superuser']
        userdata = dict()

        try:
            userdata = self.users_.get_user(username)
        except:
            raise

        return dict(zip(userkeys, userdata))

    def get_showdata(self, show_id):
        showkeys = ['name', 'description']
        showdata = dict()

        try:
            showdata = self.backend_.get_show(show_id)
        except:
            raise

        return dict(zip(showkeys, showdata))

    def get_user_shows(self, username):
        try:
            user_shows = self.backend_.get_user_shows(username)
        except:
            raise

        return user_shows

    def get_show_users(self, show_id):
        try:
            show_users = self.backend_.get_show_users(show_id)
        except:
            raise

        return show_users

    def update_user(self, kwargs):
        try:
            query = kwargs['query']
        except:
            raise ValueError(ERROR_INVALIDQUERY_MSG)

        if query == "update":
            try:
                name = kwargs['name']
                password = kwargs['password']
                active = kwargs['active']
                superuser = kwargs['superuser']
            except:
                raise ValueError(ERROR_INVALIDQUERY_MSG)

            if not password:
                try:
                    self.users_.update_user(username=name,
                                       active=active,
                                       superuser=superuser)
                except:
                    raise
            else:
                try:
                    self.users_.update_user_pw(username=name,
                                           password=password,
                                           active=active,
                                           superuser=superuser)
                except:
                    raise
        else:
            raise ValueError(ERROR_INVALIDQUERY_MSG)

        return SUCCESS_UPDATEUSER_MSG

    def update_show(self, kwargs):
        try:
            query = kwargs['query']
        except:
            raise ValueError(ERROR_INVALIDQUERY_MSG)

        if query == "update":
            try:
                show_id = kwargs['id']
                name = kwargs['name']
                description = kwargs['description']
            except:
                raise ValueError(ERROR_INVALIDQUERY_MSG)

            try:
                self.backend_.update_show(show_id,
                                          name,
                                          description)
            except:
                raise
        elif query == "add":
            try:
                show_id = kwargs['id']
                name = kwargs['user']
            except:
                raise ValueError(ERROR_INVALIDQUERY_MSG)

            try:
                self.backend_.add_user_show(show_id,
                                          name)
            except:
                raise
        else:
            raise ValueError(ERROR_INVALIDQUERY_MSG)

        return SUCCESS_UPDATESHOW_MSG


class Backend(object):

    def __init__(self):
        self.log_ = Log()

    def create_db(self):
        with sqlite3.connect(DATABASE) as c:
            c.execute(''' CREATE TABLE
                          IF NOT EXISTS 
                          stationxml(stationxml_id INTEGER PRIMARY KEY,
                                stationxml TEXT,
                                alias TEXT) ''')
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          shows(id INTEGER PRIMARY KEY,
                                name TEXT,
                                description TEXT) ''')
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          show_user(show_user_id INTEGER PRIMARY KEY,
                                    id INTEGER,
                                    username TEXT,
                                    FOREIGN KEY(id) REFERENCES shows(id),
                                    FOREIGN KEY(username) REFERENCES users(username)
                                    )''')
            c.execute(''' CREATE TABLE
                          IF NOT EXISTS
                          calendar(calendar_id INTEGER PRIMARY KEY,
                                    year INTEGER,
                                    month INTEGER,
                                    day INTEGER,
                                    hour INTEGER,
                                    length INTEGER,
                                    live INTEGER,
                                    id INTEGER,
                                    stationxml_id INTEGER,
                                    FOREIGN KEY(id) REFERENCES shows(id),
                                    FOREIGN KEY(stationxml_id) REFERENCES stationxml(stationxml_id)
                                    )''')
            self.log_.write_log(LOG_TABLESCREATED_MSG)

    def update_show(self, show_id, name, description):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' UPDATE 
                              shows
                              SET name = ?,
                                  description = ?
                              WHERE id = ? ''',
                          (name,
                           description,
                           show_id))
            except:
                raise ValueError(ERROR_UPDATESHOW_MSG)
        self.log_.write_log(LOG_UPDATEDSHOW_MSG.format(name))

    def add_user_show(self, show_id, name):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' INSERT INTO 
                              show_user(id,
                                    username) 
                              VALUES (?, ?) ''',
                          (show_id,
                           name))
            except ValueError:
                raise ValueError(ERROR_ADDUSERSHOW_MSG)
        self.log_.write_log(LOG_ADDEDUSERSHOW_MSG.format(name, show_id))



    def get_user_shows(self, username):
        result = []
        keys = ['show_name', 'show_id']
        with sqlite3.connect(DATABASE) as c:
            self.user_shows = c.execute('''SELECT shows.name, shows.id
                                          FROM shows JOIN show_user using (id)
                                          WHERE username=?''',
                                          (username,))
            try:
                for item in self.user_shows.fetchall():
                    result.append(dict(zip(keys, list(item))))
                return result
            except:
                raise ValueError(ERROR_NOSHOWSFOUND_MSG)

    def get_show_users(self, show_id):
        result = []
        with sqlite3.connect(DATABASE) as c:
            self.user_shows = c.execute('''SELECT users.username
                                          FROM users JOIN show_user using (username)
                                          WHERE id=?''',
                                          (show_id,))
            try:
                for item in self.user_shows.fetchall():
                    result.append(item[0])
                return result
            except:
                raise ValueError(ERROR_NOUSERSFOUND_MSG)


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

    def add_episode(self, data):
        with sqlite3.connect(DATABASE) as c:
            try:
                c.execute(''' INSERT INTO 
                              calendar(year,
                                       month,
                                       day,
                                       hour,
                                       length,
                                       live,
                                       id,
                                       stationxml_id) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?) ''',
                          data)
            except ValueError:
                raise ValueError(ERROR_ADDEPISODE_MSG.format(str(data)))


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
        self.log_.write_log(LOG_ADDEDSHOW_MSG.format(name, show_id))


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
        self.log_.write_log(LOG_ADDEDSTATIONXML_MSG.format(alias))
        return SUCCESS_STATIONXMLIMPORT_MSG.format(alias)

    def get_schedule(self, schedule_id):
        with sqlite3.connect(DATABASE) as c:
            result = c.execute(''' SELECT stationxml, alias
                                   FROM stationxml
                                   WHERE stationxml_id=?''',
                                   (schedule_id,))
        return result.fetchall()

    def get_schedules(self):
        result = []
        keys = ['id', 'alias']
        with sqlite3.connect(DATABASE) as c:
            self.schedules = c.execute(''' SELECT stationxml_id,alias
                                                  FROM stationxml''')
            for item in self.schedules.fetchall():
                result.append(dict(zip(keys, list(item))))
        return result


    def get_shows(self):
        result = []
        keys = ['id', 'name']
        with sqlite3.connect(DATABASE) as c:
            self.schedules = c.execute(''' SELECT id,name
                                                  FROM shows''')
            for item in self.schedules.fetchall():
                result.append(dict(zip(keys, list(item))))
        return result

    def calendar_exists(self, schedule_id):
        with sqlite3.connect(DATABASE) as c:
            result = c.execute(''' SELECT * 
                                   FROM calendar
                                   WHERE stationxml_id=?''',
                                (schedule_id,))
            for item in result.fetchall():
                if item:
                    return True
                else:
                    return False
