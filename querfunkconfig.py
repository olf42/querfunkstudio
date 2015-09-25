#!/usr/bin/env python3

import os.path

DATABASE_DIR = "database"
DATABASE_FILE = "querfunkstudio_development.db"
DATABASE = os.path.join(os.path.dirname(__file__), DATABASE_DIR, DATABASE_FILE)

LOG_TYPE = {0:"info",
            1:"warning",
            2:"error"}
LOG_DISPLAY = {0:"success",
               1:"warning",
               2:"danger"}

WEEKDAYS =   { "Mo" : 1,
               "Di" : 2,
               "Mi" : 3,
               "Do" : 4,
               "Fr" : 5,
               "Sa" : 6,
               "So" : 7,
               1: "Monday",
               2: "Tuesday",
               3: "Wednesday",
               4: "Thursday",
               5: "Friday",
               6: "Saturday",
               7: "Sunday",
               }
YES_NO =    { 0 : "No",
              1 : "Yes"
            }

BAD_CHARACTERS = '`!@#&<>?'

ERROR_BADCHARACTERS_MSG = "Username contains bad characters, such as: {0}".format(BAD_CHARACTERS)
ERROR_LOGIN_MSG = "Username not found, Password mismatch or user not active"
ERROR_SESSION_MSG = "No Username found in your Session. Please log in."
ERROR_USERCREATE_MSG = "User already exists! Choose a different Name and try again."
ERROR_PASSWORD_MSG = "Passwords don't match. Try again!"
ERROR_NOTSUPERUSER_MSG = "User is not superuser!"
ERROR_STATIONXMLIMPORT_MSG = "Import not possible. Maybe the alias already exists?"
ERROR_NOSCHEDULESFOUND_MSG = "No Schedules found."
ERROR_SCHEDULENOTFOUND_MSG = "Schedule not found."
ERROR_SHOWNOTFOUND_MSG = "Show not found."
ERROR_ADDSHOW_MSG = "Show already exists!"
ERROR_NOSHOWSFOUND_MSG = "No shows found!"
ERROR_USERNOTFOUND_MSG = "User not found!"
ERROR_NOUSERSFOUND_MSG = "No users found!"
ERROR_INVALIDQUERY_MSG = "Invalid Query."
ERROR_UPDATEUSER_MSG = "An error occured, while updating the user data."

SUCCESS_UPDATEUSER_MSG = "Update successful."
SUCCESS_STATIONXMLIMPORT_MSG = "Added {0} successfully."
SUCCESS_REGISTRATION_MSG = "Account created. Needs approval."

LOG_TABLESCREATED_MSG = "Tables created."
LOG_USERTABLESCREATED_MSG = "User tables created."
LOG_ADDEDUSER_MSG = "Added user <b>{0}</b>"
LOG_UPDATEDUSER_MSG = "Updated user <b>{0}</b> (Active: {1}; Superuser: {2})"
LOG_ADDEDSTATIONXML_MSG = "Imported stationxml <b>{0}</b>"
LOG_ADDEDSHOW_MSG = "Added show <b>{0} ({1})</b>"
