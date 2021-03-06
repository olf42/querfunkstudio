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
        self.log_ = Log()
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
    def schedules(self, **kwargs):

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        error=''
        try:
            schedule_list = self.backend_.get_schedules()
        except ValueError as e:
            return self.env.get_template('schedules.html').render(error=e)
        return self.env.get_template('schedules.html').render(schedules=schedule_list)


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
                                                           error=error)

    @cherrypy.expose
    def generate(self, **kwargs):
        error = str()
        shows = dict()
        no_of_shows = 0
        added_shows= []
        existing_shows= []
        success = str()

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        if len(kwargs)>0:
            try:
                added_shows, existing_shows, no_of_shows = self.backend_.generate_calendar(kwargs['id'])
                success = SUCCESS_ADDEDCALENDAR_MSG
            except ValueError as e:
                error=e

        return self.env.get_template('generate.html').render(added_shows=added_shows,
                                                             existing_shows=existing_shows,
                                                             no_of_shows=no_of_shows,
                                                             error=error,
                                                             success=success
                                                            )

    @cherrypy.expose
    def schedule(self, **kwargs):
        error = str()
        schedule = dict()

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        if len(kwargs)>0:
            try:
                schedule = self.backend_.get_schedule(kwargs)
            except ValueError as e:
                error=e
        else:
            error = ERROR_SCHEDULENOTFOUND_MSG

        return self.env.get_template('schedule.html').render(schedule=schedule,
                                                           error=error,
                                                           weekdays=WEEKDAYS,
                                                          )

    @cherrypy.expose
    def users(self):

        users = dict()

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        for user in self.backend_.get_users():
            users[user] = 0

        for superuser in self.backend_.get_superusers():
            users[superuser] = 1

        print(users)
        return self.env.get_template('users.html').render(users=users)

    @cherrypy.expose
    def calendar(self):

        error = str()

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        calendar = self.backend_.get_calendar()
        return self.env.get_template('calendar.html').render(calendar=calendar,
                                                             error=error)

    @cherrypy.expose
    def event(self, **kwargs):
        success = str()
        error = str()
        event = dict()

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        if len(kwargs)>0:
            # First we update the data, if necessary
            if len(kwargs)>1:
                try:
                    success = self.backend_.update_event(kwargs)
                except ValueError as e:
                    error=str(e)
            # Then we fetch data from the DB
            try:
                event_id = kwargs['id']
                event, episodes = self.backend_.get_event(event_id)
            except ValueError as e:
                error+=str(e)
        else:
            error = ERROR_EVENTNOTFOUND_MSG

        return self.env.get_template('event.html').render(event=event,
                                                           error=error,
                                                           episodes=episodes,
                                                           success=success
                                                          )


    @cherrypy.expose
    def user(self, **kwargs):

        noshows = ERROR_NOSHOWSFOUND_MSG
        shows = []
        success = str()
        error = str()

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        if len(kwargs)>0:
            # First, we update the userdata in the database
            if len(kwargs)>1:
                try:
                    success = self.backend_.update_user(kwargs)
                except ValueError as e:
                    error=str(e)
            # Then, we fetch the current userdata from the db
            try:
                userdata = self.backend_.get_userdata(kwargs['name'])
            except ValueError as e:
                error+=str(e)

        shows = self.backend_.get_user_shows(kwargs['name'])

        return self.env.get_template('user.html').render(userdata=userdata,
                                                        shows=shows,
                                                        noshows=noshows,
                                                        error=error,
                                                        success=success)


    @cherrypy.expose
    def shows(self):

        error = str()
        shows = []

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        try:
            shows = self.backend_.get_shows()
        except ValueError as e:
            error=e
        return self.env.get_template('shows.html').render(shows=shows,error=error)

    @cherrypy.expose
    def show(self, **kwargs):

        nousers = ERROR_NOUSERSFOUND_MSG
        showusers = []
        showdata = dict()
        error = str()
        success = str()
        episodes = []

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        if len(kwargs)>0:
            # First, we update the userdata in the database
            if len(kwargs)>1:
                try:
                    success = self.backend_.update_show(kwargs)
                except ValueError as e:
                    error=str(e)
            try:
                show_id = kwargs['id']
                showdata = self.backend_.get_showdata(show_id)
                episodes = self.backend_.get_episodes(show_id)
            except ValueError as e:
                error+=str(e)

        showusers = self.backend_.get_show_users(show_id)
        users = self.backend_.get_users()

        # Remove already connected users from the users to add list
        for user in showusers:
            users.pop(user)

        return self.env.get_template('show.html').render(showdata=showdata,
                                                        showusers=showusers,
                                                        users=users,
                                                        show_id=show_id,
                                                        episodes=episodes,
                                                        success=success,
                                                        error=error,
                                                        nousers=nousers)

    @cherrypy.expose
    def log(self):

        try:
            user = self.user_.superuser_authenticated()
        except ValueError as e:
            return self.env.get_template('index.html').render(error=e)

        logs = self.log_.get_log()
        for message in logs:
            message['type'] = LOG_DISPLAY[message['type']]
        return self.env.get_template('log.html').render(logs=logs)
