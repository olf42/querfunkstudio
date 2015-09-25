#!/usr/bin/env python3

import cherrypy
import os.path
import datetime
import sqlite3

from querfunkconfig import *

class Log(object):

    def create_db(self):
        with sqlite3.connect(DATABASE) as c:
            c.execute(''' CREATE TABLE 
                          IF NOT EXISTS 
                          log(id INTEGER PRIMARY KEY,
                                datetime TEXT,
                                message TEXT,
                                type INTEGER
                                ) ''')

    def write_log(self, message, logtype=0):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        with sqlite3.connect(DATABASE) as c:
            c.execute(''' INSERT INTO 
                          log(datetime,
                              message,
                              type)
                          VALUES (?, ?, ?) ''',
                          (now,
                           message,
                           logtype))

    def get_log(self):
        result = []
        keys = ["datetime", "message", "type"]
        with sqlite3.connect(DATABASE) as c:
            response = c.execute(''' SELECT datetime, message, type
                          FROM log
                          ORDER BY datetime DESC''')
        for item in response.fetchall():
            itemdict =dict(zip(keys,list(item)))
            result.append(itemdict)
        return result

