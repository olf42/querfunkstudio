#!/usr/bin/env python3

import cherrypy
import os.path
from jinja2 import Environment, PackageLoader

from querfunkconfig import *
from querfunkuser import *
from querfunktools import *
from querfunkstudio import *
from querfunkadmin import *
from querfunkbackend import *

if __name__ == '__main__':

    env = Environment(loader=PackageLoader('querfunkstudio', 'templates'))
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Test Data
    if not os.path.isfile(DATABASE):
        users_ = Users()
        users_.create_db()

        backend_ = Backend()
        backend_.create_db()

        users_.add_user(username="Thorsten",
                       password="Password",
                       active=0,
                       superuser=0)
        users_.add_user(username="olf",
                       password="Password",
                       active=1,
                       superuser=1)


    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8026,
        'server.thread_pool_max': 500,
        'server.thread_pool': 100,
        'log.screen': True
    })

    cherrypy.tree.mount(Querfunkstudio(env), "/", {
            '/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': os.path.join(current_dir, 'public'),
                  'tools.sessions.on': True,
                  'tools.sessions.storage_type' : "file",
                  'tools.sessions.storage_path' : os.path.join(current_dir, "sessions")
                  }
    })
    cherrypy.tree.mount(Querfunkadmin(env), "/admin", {
            '/': {'tools.staticdir.on': True,
                  'tools.staticdir.dir': os.path.join(current_dir, 'public'),
                  'tools.sessions.on': True,
                  'tools.sessions.storage_type' : "file",
                  'tools.sessions.storage_path' : os.path.join(current_dir, "sessions")
                  }
    })



    cherrypy.engine.start()
    cherrypy.engine.block()

