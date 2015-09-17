#!/usr/bin/env python3
# Filename: station-xml-editor.py
# Read a station xml-file and grab mp3 recordings of recently finished radio show.
# (c) Olf Tuksowitsch <olf@subsignal.org>, 4/2015, GPL v2 or v3

import sys
import datetime
import getopt
import xml.etree.ElementTree as ET
from querfunkconfig import *

class Schedule(object):

    def __init__(self):
        self.schedule = {}   # this dict contains 5 weeks/dicts
        for i in range(1,6):
            self.schedule[i] = {} # these dicts will be filled with 7 days/dicts each
            for j in range(1,8):
                self.schedule[i][j] = {}
                for k in range(24):
                    self.schedule[i][j][k] = {}

    def add_show(self,week,day,time,data):
        if (self.schedule[week][day][time] == {}):
            self.schedule[week][day][time] = data
            return 0
        else:
            raise ValueError

    def get_schedule(self):
        return self.schedule

    def get_week(self,week):
        return self.schedule[week]

    def get_days(self,day):
        '''Return all days matching the given day-id'''
        result = []
        for i in range(1,6):
            result.append(self.schedule[i][day])
        return result

    def get_day(self,week,day):
        return self.schedule[week][day]

    def get_slot(self,week,day,slot):
        return self.schedule[week][day][slot]

    def set_schedule(self, stationxmltree):
        for broadcast in stationxmltree.findall("broadcast"):
            broadcast_id = broadcast.attrib['id']
            sxml_info = broadcast.find("info")
            broadcast_name = sxml_info.find("name").text
            self.sxml_transmission = broadcast.find("transmissions")
            self.parse_shows(broadcast_name, broadcast_id, "live")
            try:
                self.parse_shows(broadcast_name, broadcast_id, "repeat")
            except:
                pass

    def parse_shows(self, name, b_id, keyword):
        for key in self.sxml_transmission.findall(keyword):
            week = int(key.find("week").text)
            day  = WEEKDAYS[key.find("day").text]
            time = int(key.find("starttime").text[:2])
            length = key.find("length").text
            try:
                self.add_show(int(week), day, time, {"id": b_id,
                                                     "length":length,
                                                     "name":name,
                                                     "live":keyword})
            except ValueError:
                print("StationXML-File contains duplicates:")
                print("Tried to add {3} in Week {0} on Day {1} at {2}:00".format(week,
                                                                     day,
                                                                     time,
                                                                     name))
                print("But this spot is already occupied by {0}".format(self.schedule[week][day][time]['name']))
                sys.exit(1)

    def get_schedule(self):
        return self.schedule

    def get_show(self, showname):
        result = []
        for i in range(1,6):
            for j in range(1,8):
                for k in range(24):
                    show = self.get_slot(i,j,k)
                    if show:
                        if (show['name']  == showname):
                            result.append(self.get_slot(i,j,k))
        return result

class ScheduleView(object):

    def __init__(self):
        self.schedule = Schedule()

    def add_show(self,week, day, time, data):
        self.schedule.add_show(week, day, time, data)

    def show_schedule(self):
        result = ''
        for i in range(1,6):
            for j in range(1,8):
                for k in range(24):
                    info = self.schedule.get_slot(i,j,k)
                    if (info == {}):
                        continue
                    result += "{0}:00 Uhr\t{2}\t{3}\t{4} - {1}<br>".format(k,
                                                                 info["name"],
                                                                 info["length"],
                                                                 info["live"],
                                                                 info["id"])
                result += "----------------------------------------<br>"
            result += "--------------------------------------------------------------------------------<br>"
        return result

    def show_days(self,day):
        '''Return all days matching the given day-id'''
        result = self.schedule.get_days(day)
        for day in result:
            for slot in day:
                print("{0}:00 Uhr\t{1}".format(slot,day[slot]))
            print("--------------------")

    def import_stationxml(self, content):
        sxml = ET.fromstring(content)

        try:
            sxml_schedule = sxml.find("schedule")
            self.schedule.set_schedule(sxml_schedule)
        except NameError as e:
            print("Unexpected error:", e)

    def show_show(self, showname):
        result = self.schedule.get_show(showname)
        for i in result:
            print(i)

    def get_schedule(self):
        return self.schedule.get_schedule()

if __name__ == "__main__":
    querfunk = ScheduleView()
    querfunk.import_stationxml(STATIONXML_FILENAME)
    print(querfunk.show_schedule())
