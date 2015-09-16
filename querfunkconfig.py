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

ERROR_LOGIN_MSG = "Username not found, Password mismatch or user not active"
ERROR_SESSION_MSG = "No Username found in your Session. Please log in."
ERROR_USERCREATE_MSG = "User already exists! Choose a different Name and try again."
ERROR_PASSWORD_MSG = "Passwords don't match. Try again!"
ERROR_NOTSUPERUSER_MSG = "User is not superuser!"
ERROR_STATIONXMLIMPORT_MSG = "Import not possible. Maybe the alias already exists?"

SUCCESS_STATIONXMLIMPORT_MSG = "Added {0} successfully."
SUCCESS_REGISTRATION_MSG = "Account created. Needs approval."
