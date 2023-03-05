# crontab.py - code to interfere with crontab
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>
#
# Ported to PyObject and Python3 by rizalmart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from gi.repository import Gio

#python modules
import re
import os
import tempfile
import string

#custom modules
import lang
import config
import gettext
import locale

from locale import gettext as _

import configparser


class Crontab:
    def __init__(self,root,user,uid,gid, user_home_dir):
		
        settings = Gio.Settings.new(config.getDconfPath())
		
        #default preview length
        self.preview_len = 50
        self.root = root
        self.set_rights(user,uid,gid, user_home_dir)
        self.user_home_dir = user_home_dir

        self.output = ["",
                        ">/dev/null 2>&1",
                        config.gs_dir + "/xwrapper.py",
                        ">/dev/null 2>&1",
                      ]

        self.crontabRecordRegex = re.compile('([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^\s]+)\s([^#\n$]*)(\s#\s([^\n$]*)|$)')
        self.__setup_timespec__()
        self.env_vars = [ ]

        self.crontabdata = self.user_home_dir + "/.config/gtock/crontab"
        self.crontabdatafileversion = 5

        if os.path.exists (self.user_home_dir + "/.config") != True:
            os.mkdir (self.user_home_dir + "/.config", mode=0o700, exist_ok=True)
            os.chown (self.user_home_dir + "/.config", self.uid, self.gid)
        if os.path.exists(self.crontabdata) != True:
            try:
                os.makedirs(self.crontabdata, mode=0o700, exist_ok=True)
                if self.root == 1:
                    os.chown (self.user_home_dir + "/.config/gtock", self.uid, self.gid)
                    os.chown (self.crontabdata, self.uid, self.gid)
            except:
                print("Failed to create data dir! Make sure ~/.config and ~/.config/gtock are writable.")



    def __setup_timespec__ (self):
        self.special = {
            "@reboot"  : '@reboot',
            "@hourly"  : '0 * * * *',
            "@daily"   : '0 0 * * *',
            "@weekly"  : '0 0 * * 0',
            "@monthly" : '0 0 1 * *',
            "@yearly"  : '0 0 1 1 *',
            "@annually": '0 0 1 1 *',
            "@midnight": '0 0 * * *'
            }

        self.timeranges = {
            "minute"   : range(0,60),
            "hour"     : range(0,24),
            "day"      : range(1,32),
            "month"    : range(1,13),
            "weekday"  : range(0,8)
            }

        self.timenames = {
            "minute"   : _("Minute"),
            "hour"     : _("Hour"),
            "day"      : _("Day of Month"),
            "month"    : _("Month"),
            "weekday"  : _("Weekday")
            }

        self.monthnames = {
            "1"        : "jan",
            "2"        : "feb",
            "3"        : "mar",
            "4"        : "apr",
            "5"        : "may",
            "6"        : "jun",
            "7"        : "jul",
            "8"        : "aug",
            "9"        : "sep",
            "10"       : "oct",
            "11"       : "nov",
            "12"       : "dec"
            }
        self.monthnumbers = {
            "jan"   : "1",
            "feb"   : "2",
            "mar"   : "3",
            "apr"   : "4",
            "may"   : "5",
            "jun"   : "6",
            "jul"   : "7",
            "aug"   : "8",
            "sep"   : "9",
            "oct"   : "10",
            "nov"   : "11",
            "dec"   : "12"
            }

        self.downames = {
            "0"        : "sun",
            "1"        : "mon",
            "2"        : "tue",
            "3"        : "wed",
            "4"        : "thu",
            "5"        : "fri",
            "6"        : "sat",
            "7"        : "sun"
            }

        self.downumbers = {
            "sun"   : "0",
            "mon"   : "1",
            "tue"   : "2",
            "wed"   : "3",
            "thu"   : "4",
            "fri"   : "5",
            "sat"   : "6",
            "sun"   : "7"
            }

    def set_rights(self,user,uid,gid, ud):
        self.user = user
        self.uid = uid
        self.gid = gid
        self.user_home_dir = ud
        self.crontabdata = self.user_home_dir + "/.config/gtock/crontab"
        if os.path.exists (self.user_home_dir + "/.config") != True:
            os.mkdir (self.user_home_dir + "/.config", mode=0o700, exist_ok=True)
            os.chown (self.user_home_dir + "/.config", self.uid, self.gid)
        if os.path.exists(self.crontabdata) != True:
            try:
                os.makedirs(self.crontabdata, mode=0o700, exist_ok=True)
                if self.root == 1:
                    os.chown (self.user_home_dir + "/.config/gtock", self.uid, self.gid)
                    os.chown (self.crontabdata, self.uid, self.gid)
            except:
                print (_("Failed to create data dir: %s. Make sure ~/.config and ~/.config/gtock are writable.") % (self.crontabdata))

    def get_type (self):
        return "crontab"

    def checkfield (self, expr, type):
        """Verifies format of Crontab timefields

        Checks a single Crontab time expression.
        At first possibly contained alias names will be replaced by their
        corresponding numbers. After that every asterisk will be replaced by
        a "first to last" expression. Then the expression will be splitted
        into the comma separated subexpressions.

        Each subexpression will run through:
        1. Check for stepwidth in range (if it has one)
        2. Check for validness of range-expression (if it is one)
        3. If it is no range: Check for simple numeric
        4. If it is numeric: Check if it's in range

        If one of this checks failed, an exception is raised. Otherwise it will
        do nothing. Therefore this function should be used with
        a try/except construct.
        """

        # reboot?
        if type == "special":
            if expr in self.special:
                pass
            else:
                raise ValueError ("special", _("Basic"), _("This is not a valid special record: %(record)s") % {"record": expr})
        else:
            timerange = self.timeranges[type]

            # Replace alias names only if no leading and following alphanumeric and
            # no leading slash is present. Otherwise terms like "JanJan" or
            # "1Feb" would give a valid check. Values after a slash are stepwidths
            # and shouldn't have an alias.
            if type == "month": alias = self.monthnames.copy()
            elif type == "weekday": alias = self.downames.copy()
            else: alias = None
            if alias != None:
                while True:
                    try: key,value = alias.popitem()
                    except KeyError: break
                    expr = re.sub("(?<!\w|/)" + value + "(?!\w)", key, expr)

            expr = expr.replace("*", str(min(timerange)) + "-" + str(max(timerange)) )

            list = expr.split(",")
            rexp_step = re.compile("^(\d+-\d+)/(\d+)$")
            rexp_range = re.compile("^(\d+)-(\d+)$")

            for field in list:
                result = rexp_step.match(field)
                if  result != None:
                    field = result.groups()[0]
                    if int(result.groups()[1]) not in timerange:
                        raise ValueError("stepwidth", self.timenames[type], _("Must be between %(min)s and %(max)s") % { "min": min(timerange), "max": max(timerange) } )

                result = rexp_range.match(field)
                if (result != None):
                    if (int(result.groups()[0]) not in timerange) or (int(result.groups()[1]) not in timerange):
                        raise ValueError("range", self.timenames[type], _("Must be between %(min)s and %(max)s") % { "min": min(timerange), "max": max(timerange) } )
                elif field.isdigit() != True:
                    raise ValueError("fixed", self.timenames[type], _("%s is not a number") % ( field ) )
                elif int(field) not in timerange:
                    raise ValueError("fixed", self.timenames[type], _("Must be between %(min)s and %(max)s") % { "min": min(timerange), "max": max(timerange) } )


    def update (self, minute, hour, day, month, weekday, command, linenumber, parentiter, output, job_id, comment, title, desc):
        if self.check_command (command) == False:
            return False

        # update crontab

        easystring = self.__easy__ (minute, hour, day, month, weekday)

        if job_id == False:
            ## Create a job_id for an existing task
            f = os.path.join (self.crontabdata, "last_id") 
            if os.access (f, os.R_OK):
                fh = open (f, 'r+')
                r = fh.read ()
                if r == "":
                    last_id = 1
                else:
                    last_id = int (r)

                #print "last_id" + str (last_id)
                job_id = last_id + 1
                #print "job_id" + str (job_id)
                fh.seek (0)
                fh.truncate (1)
                fh.write (str(job_id))
                fh.close ()
            else:
                job_id = 1
                fh = open (f, 'w')
                fh.write ('1')
                fh.close ()

            os.chown (f, self.uid, self.gid)
            os.chmod (f, mode=0o600)

        record = command
        display = "0"
        if output == 1:
            space = " "
            if record[len(record)-1] == " ":
                space = ""
            record = record + space + self.output[1]
        elif (output == 2) or (output == 3):
            display = os.getenv ('DISPLAY')
            record = config.xwrapper_exec + " c " + str(job_id)
            if output == 3:
                record = record + " " + self.output [3]

        if minute == "@reboot":
            record = "@reboot " + record
        else:
            record = minute + " " + hour + " " + day + " " + month + " " + weekday + " " + record

        record = record + " # JOB_ID_" + str (job_id)

        if title == None:
            title = _("Untitled")

        f = os.path.join (self.crontabdata, str(job_id)) + ".info"
        #print f
        fh = open (f, 'w')
        fh.truncate(1)
        fh.seek (0)
        fh.write ("ver=" + str(self.crontabdatafileversion) + "\n")
        fh.write ("title=" + title + "\n")
        fh.write ("desc=" + desc + "\n")
        fh.write ("output=" + str (output) + "\n")
        fh.write ("display=" + display + "\n")
        fh.write ("command_d=" + command + "\n")
        fh.close ()
        
        os.chown (f, self.uid, self.gid)
        os.chmod (f, mode=0o600)

        self.lines[linenumber] = record

        # TODO: let write trow an exception if failed
        self.__write__ ()


    def delete (self, linenumber, iter, job_id):
        # delete file
        f = os.path.join (self.crontabdata, job_id) + ".info"
        if os.access(f, os.F_OK):
            os.unlink (f)

        number = 0
        newlines = list ()
        for line in self.lines:
            if number != linenumber:
                newlines.append (line)
            number = number + 1

        self.lines = newlines
        # TODO: let write trow an exception if failed
        self.__write__ ()


    def append (self, minute, hour, day, month, weekday, command, output, title, desc = None):
		
        if self.check_command (command) == False:
            return False

        if title == None:
            title = _("Untitled")

        if desc == None:
            desc = ""
  
        
            
        r=self.settings.get_int("crontab-last-id")
        
        if r == 0:
           last_id = 1
        else:
           last_id = int (r)

        job_id = last_id + 1
            
        self.settings.set_int("crontab-last-id",job_id)

        record = command
        display = "0"
        
        if output == 1:
            space = " "
            if record[len(record)-1] == " ":
                space = ""
            record = record + space + self.output[1]
        elif (output == 2) or (output == 3):
            display = os.getenv ('DISPLAY')
            record = config.xwrapper_exec + " c " + str (job_id)
            if output == 3:
                record = record + " " + self.output [3]

        if minute == "@reboot":
            record = "@reboot " + record
        else:
            record = minute + " " + hour + " " + day + " " + month + " " + weekday + " " + record

        record = record + " # JOB_ID_" + str (job_id)

        self.lines.append (record)

        f = os.path.join (self.crontabdata, str(job_id)) + ".info"
        fh = open (f, 'w')
        fh.truncate (1)
        fh.seek (0)
        fh.write ("ver=" + str(self.crontabdatafileversion) + "\n")
        fh.write ("title=" + title + "\n")
        fh.write ("desc=" + desc + "\n")
        fh.write ("output=" + str(output) + "\n")
        fh.write ("display=" + display + "\n")
        fh.write ("command_d=" + command + "\n")
        fh.close ()
        os.chown (f, self.uid, self.gid)
        os.chmod (f, mode=0o600)
        # TODO: let write trow an exception if failed
        self.__write__ ()


    #check command for problems
    def check_command (self, command):
        # check if % is part of the command and if it is escaped, and the escapor not escaped.
        i = command.find ("%")
        while i != -1:
            escaped = 0
            part = command[0:i]
            command = command[i + 1:]
            e = part.rfind ("\\")
            while (e != -1) and (e == len(part) - 1):
                escaped = escaped + 1
                part = part[0:len(part) - 1]
                e = part.rfind ("\\")

            if (escaped % 2 == 0):
                return False

            i = command.find ("%")
        return True

    #read tasks in crontab
    def read (self, easy = True):
		
     if config.cronTabInstalled()==False:
        return
     else:	

        data = []

        if self.root:
            execute = config.getCrontabbin () + " -l -u " + self.user
        else:
            execute = config.getCrontabbin () + " -l"

        linecount = 0
        self.lines = os.popen(execute).readlines()
        for line in self.lines:
            #read line and get info
            array_or_false = self.parse(line)
            if array_or_false != False:
                if array_or_false[0] == 2:
                    (minute, hour, day, month, weekday, command, comment, job_id, title, desc, output, display) = array_or_false[1]

                    time = minute + " " + hour + " " + day + " " + month + " " + weekday

                    #make the command smaller if the lenght is to long
                    preview = self.__make_preview__ (command)

                    #add task to treemodel in mainWindow
                    if easy:
                      easy_s = self.__easy__ (minute, hour, day, month, weekday)
                    else:
                      easy_s = ""

                    if minute == "@reboot":
                      data.append([title, easy_s , preview, line, linecount, time, self, None, job_id, "", "","", _("Recurrent"), "crontab", output, _("At reboot")])
                    else:
                      data.append([title, easy_s, preview, line, linecount, time, self, None, job_id, "", "","", _("Recurrent"), "crontab", output, time])


            linecount = linecount + 1


        return data


    def translate_frequency (self, frequency):

        if frequency == "minute":
            return _("minute")
        if frequency == "hour":
            return _("hour")
        if frequency == "day":
            return _("day")
        if frequency == "month":
            return _("month")
        if frequency == "weekday":
            return _("weekday")

        return frequency


    #get info out of task line
    def parse (self, line, nofile = False):
        # nofile: no datafile for title and icon available

        # Format of gtock job line
        # * * * * * ls -l >/dev/null >2&1 # JOB_ID_1

        # Return types
        # 0: Special expression
        # 1: Enivornment variable
        # 2: Standard expression
        # 3: Comment

        origline = line
        line = line.lstrip()
        comment = ""


        if line != "":
            #print "Parsing line: " + line
            if line[0] == "#":
                comment = line[1:]
                line = ""
                return [3, comment]
            else:
                if (line.find ('#') != -1):
                    line, comment = line.rsplit('#', 1)

            comment = comment.strip ()
            line = line.strip ()

        if line == "":
            #Empty
            if comment != "":
                return [3, comment]
            else:
                return False
        #special expressions
        elif line[0] == "@":
            special_expression, line = self.get_exp_sec (line)

            if special_expression == "@reboot":
                minute = "@reboot"
                hour = "@reboot"
                dom = "@reboot"
                moy = "@reboot"
                dow = "@reboot"
            else:

                if special_expression in self.special:
                    expr = self.special[special_expression]
                    line = expr + " " + line

                    # Minute
                    minute, line = self.get_exp_sec (line)

                    # Hour
                    hour, line = self.get_exp_sec (line)

                    # Day of Month
                    dom, line = self.get_exp_sec (line)

                    # Month of Year
                    moy, line = self.get_exp_sec (line)

                    # Day of Week
                    dow, line = self.get_exp_sec (line)


        elif (line[0].isalpha()):
            if line[0] != '*':
                #ENVIRONMENT VARIABLE
                return [1, line]
        else:
            # Minute
            minute, line = self.get_exp_sec (line)

            # Hour
            hour, line = self.get_exp_sec (line)

            # Day of Month
            dom, line = self.get_exp_sec (line)
            # Crontab bug? Let's not support
            # dom behaves like minute
            """
            dom = self.day
            if dom.isdigit() == False:
                dom = dom.lower ()
                for day in self.scheduler.downumbers:
                    dom = dom.replace (day, self.scheduler.downumbers[day])
            """
            try:
                self.checkfield (dom, "day")
            except ex:
                print("Failed to parse the Day of Month field, possibly due to a bug in crontab.")
                return

            # Month of Year
            moy, line = self.get_exp_sec (line)
            if moy.isdigit () == False:
                moy = moy.lower ()
                for m in self.monthnumbers:
                    moy = moy.replace (m, self.monthnumbers[m])


            # Day of Week
            dow, line = self.get_exp_sec (line)
            if dow.isdigit() == False:
                dow = dow.lower ()
                for day in self.downumbers:
                    dow = dow.replace (day, self.downumbers[day])



        command = line.strip ()

        # Retrive jobid
        i = comment.find ('JOB_ID_')
        if (i != -1):
            job_id = int (comment[i + 7:].rstrip ())
        else:
            job_id = False


        # Retrive title and icon data
        if nofile == False:
            if job_id:
                success, ver, title, desc, output, display, command_d = self.get_job_data (job_id)
            else:
                success = True
                ver = 1
                title = ""
                desc = ""
                output = 0
                display = ""
                command_d = ""

            if (output == 1) or (output == 3):
                # remove devnull part of command
                # searching reverse, and only if output is saved in the datafile
                pos = command.rfind (self.output[1])
                if pos != -1:
                    command = command[:pos]
            if output >= 2:
                # rely on command from datafile, command from crontab line only contains xwrapper stuff
                command = command_d

            # support older datafiles/entries without removing the no output tag
            if ver <= 1:
                # old version, no output declaration in datafile, migration
                pos = command.rfind (self.output[1])
                if pos != -1:
                    command = command[:pos]
                    output = 1
                else:
                    output = 0

            command = command.strip()
            

            return [2, [minute, hour, dom, moy, dow, command, comment, str(job_id), title, desc, output, display]]
        else:
            return minute, hour, dom, moy, dow, command

    def get_job_data (self, job_id):
        f = os.path.join (self.crontabdata, str (job_id)) + ".info"
        if os.access (f, os.R_OK):
            fh = open (f, 'r')
            d = fh.read ()

            ver_p = d.find ("ver=")
            if ver_p == -1:
                ver = 1
            else:
                ver_s = d[ver_p + 4:d.find ("\n")]
                d = d[d.find ("\n") + 1:]
                ver = int (ver_s)

            title = d[6:d.find ("\n")]
            d = d[d.find ("\n") + 1:]

            if ver < 3:
                # not in use, is discarded
                icon = d[5:d.find ("\n")]
                d = d[d.find ("\n") + 1:]

            desc = d[5:d.find ("\n")]
            d = d[d.find ("\n") + 1:]

            output = 0
            if (ver >= 2) and (ver < 4):
                output_str = d[9:d.find ("\n")]
                output = int (output_str)
                d = d[d.find("\n")]

            if ver >= 4:
                output_str = d[7:d.find ("\n")]
                output = int (output_str)
                d = d[d.find ("\n") + 1:]

            display = ""
            if ver >= 4:
                display = d[8:d.find ("\n")]
                d = d[d.find ("\n") + 1:]
                if (len (display) < 1) or (output < 2):
                    display = ""

            command_d = ""
            if ver >= 5:
                command_d = d[10:d.find ("\n")]
                d = d[d.find ("\n") + 1:]
                if (len (command_d) < 1) or (output < 2):
                    command_d = ""

            fh.close ()
            
            

            return True, ver, title, desc, output, display, command_d

        else:
            return False, 0, "", "", 0, "", ""

    def get_exp_sec (self, line):
        line = line.lstrip ()
        #print "line: \"" + line + "\""

        ## find next whitespace
        i = 0
        found = False
        while (i < len(line)) and (found == False):
            if line[i] in string.whitespace:
                found = True
                #print "found: " + str (i)
            else:
                i = i + 1
        sec = line[0:i]
        #print "sec: \"" + sec + "\""
        line = line[i + 1:]
        return sec, line

    def __easy__ (self, minute, hour, day, month, weekday):
        return lang.translate_crontab_easy (minute, hour, day, month, weekday)


    #create temp file with old tasks and new ones and then update crontab
    def __write__ (self):
        tmpfile = tempfile.mkstemp ()
        fd, path = tmpfile
        tmp = os.fdopen(fd, 'w')
        count = 0
        for line in self.lines:

            ## Ignore the first three comments:

            ## DO NOT EDIT THIS FILE - edit the master and reinstall.
            ## (/tmp/crontab.XXXXXX installed on Xxx Xxx  x xx:xx:xx xxxx)
            ## (Cron version -- $Id$)

            if not (count < 3 and len(line) > 1 and line[0] == "#"):
                tmp.write (line)
                if line[len(line)-1] != '\n':
                    tmp.write ("\n")
            count = count + 1

        tmp.close ()

        #replace crontab config with new one in file
        if self.root:
            #print(config.getCrontabbin () + " " + path + " -u " + self.user)
            os.system (config.getCrontabbin () + " -u " + self.user + " " + path )
        else:
            # print config.getCrontabbin () + " " + path
            os.system (config.getCrontabbin () + " " + path)

        os.unlink (path)


    def __make_preview__ (self, str, preview_len = 0):
        if preview_len == 0:
            preview_len = self.preview_len

        str = str.replace ("&", "&amp")

        if len (str) <= preview_len:
            return str
        else:
            return str[:preview_len] + "..."


