# at.py - code to interfere with at
#
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

#python modules
import re
import os
from subprocess import Popen, PIPE
import sys
import tempfile
#import commands
import subprocess
import time
import datetime

#custom modules
import config


import gettext
import locale

from locale import gettext as _ 



class At:
    def __init__(self,root,user,uid,gid,user_home_dir,manual_poscorrect):

        #default preview length
        self.preview_len = 50
        self.root = root
        self.set_rights(user,uid,gid, user_home_dir)
        self.user_home_dir = user_home_dir
        self.manual_poscorrect = manual_poscorrect


        # 16       2006-01-08 13:01 a gaute
        # 7       Sun Jan  8 13:01:00 2006 a pvanhoof
        # 1 2006-04-26 08:54 a gaute
        # 14    2006-09-21 10:54 a gaute
        # 3 Tue May  8 01:01:00 2007 a gaute
        #
        # FreeBSD:
        #Date                Owner        Queue    Job#
        #Fri Sep 30 23:40:00 MSK 2011    rm              c    2


        self.sysname = os.uname ()[0]

        # FreeBSD atq output, parser ignores time zone information
        if self.sysname == 'FreeBSD':
          self.atRecordRegex = re.compile ('^(?P<dow>[\w]{3})[\s](?P<month>[\w]{3})[\s](?P<day>[0-9]+)[\s](?P<time>[0-2][0-9]:[0-5][0-9]:[0-5][0-9])[\s](?:(?P<tzone>.*)[\s]|)(?P<year>[0-9]{4})[\t]+(?P<user>.+)[\s]+(?P<class>[a-z]|[A-Z])[\t](?P<jobid>[0-9]*)$')
          # after you add a job, this line is printed to stderr
          # Job 5 will be executed using /bin/sh
          self.atRecordRegexAdd = re.compile('^Job[\s](?P<jobid>[0-9]+)[\s]will')

        # General Linux atq output
        else:
          self.atRecordRegex = re.compile('^(?P<jobid>[\d]+)[\t](?P<dow>[\w]{3,3})[\s](?P<month>[\w]{3,3})[\s]*(?P<day>[\d]+)[\s](?P<time>[\d]{2,2}[:][\d]{2,2}[:][\d]{2,2})[\s](?P<year>[\d]{4,4})[\s](?P<class>[\w])[\s](?P<user>[\w]+)')
          # after you add a job, this line is printed to stderr
          # job 10 at 2006-09-18 12:38
          self.atRecordRegexAdd = re.compile('^job\s(?P<jobid>[0-9]+)\sat')

        self.SCRIPT_DELIMITER = "###### ---- GNOME_SCHEDULE_SCRIPT_DELIMITER #####"

        self.DISPLAY = "DISPLAY=%s; export DISPLAY;\n"
        self.DISPLAY = self.DISPLAY + "XAUTHORITY=" + user_home_dir + "/.Xauthority; export XAUTHORITY;\n"
        self.DISPLAY = self.DISPLAY + config.xwrapper_exec + " a\n"
        self.DISPLAY = self.DISPLAY + """
xwrapper=$?;
if [ $xwrapper -eq 0 ]; then
    echo "all fine";
else
    echo "xwrapper failed.";
    exit;
fi
"""

        # If normally this variable is unset the user would not expect it
        # to be set, which it will be because Gnome Schedule needs it.
        # Therefore we unset it in the script.
        self.POSIXLY_CORRECT_UNSET = "unset POSIXLY_CORRECT\n"

        # Environment used for executing 'at' to ensure reliable output
        # Setting locale to C
        self.at_env = os.environ.copy ()
        self.at_env["LC_ALL"] = "C"
        self.PREPEND_SCRIPT = "LC_ALL=%s; export LC_ALL\n" % os.environ.get ("LC_ALL", "")
        self.PREPEND_SCRIPT_LINES = 1

        self.atdatafileversion = 6
        self.atdata = self.user_home_dir + "/.config/gnome-schedule/at"
        if os.path.exists (self.user_home_dir + "/.config") != True:
            os.mkdir (self.user_home_dir + "/.config", mode=0o700, exist_ok=True)
            os.chown (self.user_home_dir + "/.config", self.uid, self.gid)
        if os.path.exists(self.atdata) != True:
            try:
                os.makedirs(self.atdata, mode=0o700, exist_ok=True)
                if self.root == 1:
                    os.chown (self.user_home_dir + "/.config/gnome-schedule", self.uid, self.gid)
                    os.chown (self.atdata, self.uid, self.gid)
            except:
                print("Failed to create data dir! Make sure ~/.config and ~/.config/gnome-schedule are writable.")

        self.months = {
            'Jan' : '1',
            'Feb' : '2',
            'Mar' : '3',
            'Apr' : '4',
            'May' : '5',
            'Jun' : '6',
            'Jul' : '7',
            'Aug' : '8',
            'Sep' : '9',
            'Oct' : '10',
            'Nov' : '11',
            'Dec' : '12'
        }

    def set_rights(self,user,uid,gid, ud):
        self.user = user
        self.uid = uid
        self.gid = gid
        self.user_home_dir = ud
        self.atdata = self.user_home_dir + "/.config/gnome-schedule/at"
        if os.path.exists (self.user_home_dir + "/.config") != True:
            os.mkdir (self.user_home_dir + "/.config", mode=0o700, exist_ok=True)
            os.chown (self.user_home_dir + "/.config", self.uid, self.gid)
        if os.path.exists(self.atdata) != True:
            try:
                os.makedirs(self.atdata, mode=0o700, exist_ok=True)
                if self.root == 1:
                    os.chown (self.user_home_dir + "/.config/gnome-schedule", self.uid, self.gid)
                    os.chown (self.atdata, self.uid, self.gid)
            except:
                print (_("Failed to create data dir: %s. Make sure ~/.config and ~/.config/gnome-schedule are writable.") % (self.atdata))


    def get_type (self):
        return "at"

    def parse (self, line, output = True):
        if (output == True):
            if len(line) > 1 and line[0] != '#':
                m = self.atRecordRegex.match(line.decode())
                if m != None:
                    # Time
                    time = m.group('time')

                    # FreeBSD:
                    # We are ignoring timezone and hope everything works
                    # out in the end.

                    # Date
                    day = m.group('day')
                    month = m.group ('month')

                    for monthname in self.months:
                        month = month.replace (monthname, self.months[monthname])

                    if int (day) < 10:
                        day = "0" + day
                    if int (month) < 10:
                        month = "0" + month

                    date = day + "." + month + "." + m.groups ()[5]

                    job_id = m.group ('jobid')
                    class_id = m.group ('class')
                    user = m.group ('user')

                    success, title, desc, manual_poscorrect, output, display, stdlocale = self.get_job_data (int (job_id))
                    # manual_poscorrect is only used during preparation of script

                    execute = config.getAtbin() + " -c " + job_id
                    # read lines and detect starter
                    script = Popen(execute, shell = True, env = self.at_env, stdout = PIPE).stdout.read()
                    script,  dangerous = self.__prepare_script__ (script, manual_poscorrect, output, display, stdlocale)

                    #removing ending newlines, but keep one
                    #if a date in the past is selected the record is removed by at, this creates an error, and generally if the script is of zero length
                    # TODO: complain about it as well
                    script = script.decode()

                    return job_id, date, time, class_id, user, str(script), title, dangerous, output

        elif (output == False):
            if len (line) > 1 and line[0] != '#':
                m = self.atRecordRegexAdd.search(line.decode())
                #print "Parsing line: " + line
                if m != None:
                    #print "Parse successfull, groups: "
                    #print m.groups()
                    job_id = m.group('jobid')
                    return int(job_id)
                else:
                    return False

        return False
        # TODO: throw exception

    def get_job_data (self, job_id):
        f = os.path.join (self.atdata, str (job_id)) + ".at"
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

            # icons out
            if ver < 2:
                icon = d[5:d.find ("\n")]
                d = d[d.find ("\n") + 1:]

            desc = d[5:d.find ("\n")]
            d = d[d.find ("\n") + 1:]

            manual_poscorrect_b = False
            if ver > 2:
                manual_poscorrect = d[18:d.find ("\n")]
                d = d[d.find ("\n") + 1:]
                if manual_poscorrect == "true":
                    manual_poscorrect_b = True
                elif manual_poscorrect == "false":
                    manual_poscorrect_b = False

            if ver >= 5:
                output_str = d[7:d.find ("\n")]
                output = int (output_str)
                d = d[d.find("\n") + 1:]
            else:
                output = 0

            if ver >= 5:
                display = d[8:d.find ("\n")]
                d = d[d.find ("\n") + 1:]
                if (len (display) < 1) or (output == 0):
                    display = ""
            else:
                display = ""

            if ver >= 6:
                stdlocale = True
            else:
                stdlocale = False

            fh.close ()

            return True, title, desc, manual_poscorrect_b, output, display, stdlocale

        else:
            return False, "", "", False, 0, "", False

    def write_job_data (self, job_id, title, desc, output, display):
        # Create and write data file
        f = os.path.join (self.atdata, str(job_id)) + ".at"
        fh = open (f, 'w')
        fh.truncate (1)
        fh.seek (0)
        fh.write ("ver=" + str(self.atdatafileversion) + "\n")
        fh.write ("title=" + title + "\n")
        fh.write ("desc=" + desc + "\n")

        # This one doesn't need to be passed independently for each job since the job data is only updated together with a task being appended or updated (also new added), and the variable depends on each session. Not job.
        if self.manual_poscorrect == True:
            fh.write ("manual_poscorrect=true\n")
        else:
            fh.write ("manual_poscorrect=false\n")

        fh.write ("output=" + str (output) + "\n")
        fh.write ("display=" + display + "\n")

        fh.close ()
        os.chown (f, self.uid, self.gid)
        os.chmod (f, mode=0o600)

    def checkfield (self, runat):
        regexp1 = re.compile ("([0-9][0-9])([0-9][0-9])\ ([0-9][0-9])\.([0-9][0-9])\.([0-9][0-9][0-9][0-9])")
        regexp2 = re.compile("([0-9][0-9])([0-9][0-9])")
        regexp3 = re.compile("([0-9][0-9])\.([0-9][0-9])\.([0-9][0-9][0-9][0-9])")

        runat_g1 = regexp1.match(runat)
        runat_g2 = regexp2.match(runat)
        runat_g3 = regexp3.match(runat)
        ctime = time.localtime()
        cyear = ctime[0]
        cmonth = ctime[1]
        cday = ctime[2]
        chour = ctime[3]
        cminute = ctime[4]

        if runat_g1:
            (hour, minute, day, month, year) =  runat_g1.groups()
            hour = int(hour)
            minute = int(minute)
            year = int(year)
            month = int(month)
            day = int(day)

            if hour > 24 or hour < 0:
                return False, "hour"

            if minute > 60 or minute < 0:
                return False, "minute"

            if month > 12 or month < 0:
                return False, "month"

            if day > 31 or day < 0:
                return False, "day"

            if year < 0:
                return False, "year"

            if year >= cyear:
                if year == cyear:
                    syear = True
                    if (month >= cmonth):
                        if month == cmonth:
                            smonth = True
                            if day >= cday:
                                if day == cday:
                                    sday = True
                                    if hour >= chour:
                                        if hour == chour:
                                            shour = True
                                            if minute <= cminute:
                                                return False, "minute"
                                        else:
                                            shour = False
                                    else:
                                        return False, "hour"
                                else:
                                    sday = False
                            else:
                                return False, "day"
                        else:
                            smonth = False
                    else:
                        return False, "month"
                else:
                    syear = False
            else:
                return False, "year"

        elif runat_g2:

            (hour, minute) =  runat_g2.groups()
            hour = int(hour)
            minute = int(minute)
            if hour > 24 or hour < 0:
                return False, "hour"

            if minute > 60 or minute < 0:
                return False, "minute"


        elif runat_g3:

            (day, month, year) =  runat_g3.groups()
            year = int(year)
            month = int(month)
            day = int(day)
            if year < cyear:
                return False, "year"
            if month < cmonth:
                return False, "month"
            if day < cday:
                return False, "day"

        else:
            #lowercase
            runat = runat.lower()

            #some timespecs:
            days = ['sun','mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sunday','monday','tuesday','wednesday','thursday','friday','saturday']
            relative_days = ['tomorrow','next week','today']
            relative_hour = ['noon','teatime','midnight','next hour']
            relative_minute = ['next minute']
            relative_month = ['next month']

            if runat in days:
                pass
            elif runat in relative_days:
                pass
            elif runat in relative_hour:
                pass
            elif runat in relative_minute:
                pass
            elif runat in relative_month:
                pass
            else:
                return False, "other"

        return True, "ok"


    def append (self, runat, command, title, output):
        tmpfile = tempfile.mkstemp ()
        fd, path = tmpfile
        tmp = os.fdopen(fd, 'w')
        tmp.write (self.SCRIPT_DELIMITER + "\n")
        tmp.write (self.PREPEND_SCRIPT)
        if self.manual_poscorrect:
            tmp.write (self.POSIXLY_CORRECT_UNSET)

        display = ""
        if output > 0:
            display = os.getenv ('DISPLAY')
            tmp.write (self.DISPLAY %  display )

        tmp.write (command + "\n")
        tmp.close ()

        temp = None

        if self.root == 1:
            if self.user != "root":
                #changes the ownership
                os.chown(path, self.uid, self.gid)
                execute = config.getSubin() + " " + self.user + " -c \"" + config.getAtbin() +  " -f " + path + " " + runat + " && exit\""
            else:
                execute = config.getAtbin() + " -f " + path + " " + runat
        else:
            execute = config.getAtbin() + " -f " + path + " " + runat

        p = Popen (execute, shell = True, env = self.at_env, stdin = PIPE, stdout = PIPE, stderr = PIPE, close_fds = True)
        (child_stdin, child_stdout, child_stderr) = (p.stdin, p.stdout, p.stderr)

        err = child_stderr.readlines ()
        job_id = 0
        for line in err:
            t = self.parse (line, False)
            if t != False:
                job_id = t

        #print job_id

        desc = ""
        self.write_job_data (job_id, title, desc, output, display)

        os.unlink (path)


    def update (self, job_id, runat, command, title, output):
        #print "update" + str (job_id) + runat + command + title
        #remove old
        f = os.path.join (self.atdata, str (job_id)) + ".at"
        if os.access (f, os.F_OK):
            os.unlink (f)
        execute = config.getAtrmbin()+ " " + str(job_id)
        subprocess.getoutput(execute)

        #add new
        tmpfile = tempfile.mkstemp ()
        fd, path = tmpfile
        tmp = os.fdopen(fd, 'w')

        tmp.write (self.SCRIPT_DELIMITER + "\n")
        tmp.write (self.PREPEND_SCRIPT)
        if self.manual_poscorrect:
            tmp.write (self.POSIXLY_CORRECT_UNSET)

        display = ""
        if output > 0:
            display = os.getenv ('DISPLAY')
            tmp.write (self.DISPLAY %  display )

        tmp.write (command + "\n")
        tmp.close ()

        if self.root == 1:
            if self.user != "root":
                #changes the ownership
                os.chown(path, self.uid, self.gid)
                execute = config.getSubin() + " " + self.user + " -c \"" + config.getAtbin() +  " -f " + path + " " + runat + " && exit\""
            else:
                execute = config.getAtbin() + " -f " + path + " " + runat
        else:
            execute = config.getAtbin() + " -f " + path + " " + runat

        p = Popen (execute, shell = True, env = self.at_env, stdin = PIPE, stdout = PIPE, stderr = PIPE, close_fds = True)
        (child_stdin, child_stdout, child_stderr) = (p.stdin, p.stdout, p.stderr)

        err = child_stderr.readlines ()
        job_id = 0
        for line in err:
            t = self.parse (line, False)
            if t != False:
                job_id = t

        #print job_id

        desc = ""
        self.write_job_data (job_id, title, desc, output, display)

        os.unlink (path)


    def delete (self, job_id, iter):
        if job_id:
            # delete file
            f = os.path.join (self.atdata, str(job_id)) + ".at"
            if os.access(f, os.F_OK):
                os.unlink (f)
            execute = config.getAtrmbin()+ " " + str(job_id)
            subprocess.getoutput(execute)


    def read (self):
        data = []
        #do 'atq'
        execute = config.getAtqbin ()
        self.lines = Popen(execute, shell = True, env = self.at_env, stdout = PIPE).stdout.readlines()

        # Skip header: Date..
        if self.sysname == 'FreeBSD':
            self.lines = self.lines[1:]

        for line in self.lines:
            array_or_false = self.parse (line)
            #print array_or_false
            if array_or_false != False:
                (job_id, date, time, class_id, user, lines, title, dangerous, output) = array_or_false


                preview = self.__make_preview__ (lines)
                if dangerous == 1:
                        preview = _("Warning! Unknown task: %(preview)s") % {'preview':  preview}
                #chopping of script delimiter
                lines.strip ()

                timestring = "%s %s" % (date, time)

                date_o = datetime.datetime.strptime (date + " " + time, "%d.%m.%Y %H:%M:%S")
                timestring_show = _("On %(timestring)s") % { 'timestring' : date_o.strftime ("%c") }


                # TODO: looks like it could be one append
                if self.root == 1:
                    if self.user == user:
                        data.append([title, timestring_show, preview, lines, int(job_id), timestring, self, None, date, class_id, user, time, _("Once"), "at", output, timestring])
                    else:
                        #print "Record omitted, not current user"
                        pass
                else:
                    data.append([title, timestring_show, preview, lines, int(job_id), timestring, self, None, date, class_id, user, time, _("Once"), "at", output, timestring])

                #print("added %(id)s") % { "id": job_id   }
            else:
                print("Warning: a line in atq's output didn't parse:")
                print(line)
        return data


    def __prepare_script__ (self, script, manual_poscorrect, output, display, stdlocale):

        # It looks like at prepends a bunch of stuff to each script
        # Luckily it delimits that using two newlines
        # So assuming that at never prepends two newlines unless
        # it's done prepending, we will start recording the custom commands
        # once the first two lines have been found

        # Later: It now seems like this is incorrect, and may vary upon distribution. I therefore determine the prepended stuff by making a test job and then removing the length of it. in gentoo it adds to newlines at the end of the script

        # If the script is created by Gnome Schedule the script is seperated by a delimiter.

        dangerous = 0
        scriptstart = script.find(self.SCRIPT_DELIMITER.encode())

        if scriptstart != -1:
            script = script[scriptstart:]

            if stdlocale:
                script = script[self.PREPEND_SCRIPT_LINES:]

            if manual_poscorrect == True:
                scriptstart = script.find(self.POSIXLY_CORRECT_UNSET.encode())
                if scriptstart != -1:
                    script = script[scriptstart + len(self.POSIXLY_CORRECT_UNSET):]
            else:
                script = script[len(self.SCRIPT_DELIMITER) + 1:]

            if output > 0:
                scriptstart = script.find(self.DISPLAY.encode() % display.encode())
                if scriptstart != -1:
                    script = script [scriptstart + len (self.DISPLAY % display):]

        else:
            dangerous = 1

            string = " || {\n    echo 'Execution directory inaccessible' >&2\n   exit 1\n}\n"
            string_len = len(string)
            start = script.find(string)
            start = start + string_len
            script = script[start:]
            prelen = 0
            # If the string contains TITLE=
            titlestart = script.find ("TITLE=")
            if titlestart != -1:
                titleend = script.find("\n", titlestart)
                title = script[(titlestart + 6):titleend]
                #remeber the length to remove this from the preview
                prelen = len(title) + 7
            else:
                title = _("Untitled")
            # If the string contains ICON=
            iconstart = script.find ("ICON=")
            if iconstart != -1:
                iconend = script.find ("\n", iconstart)
                icon = script[(iconstart + 5):iconend]

                prelen = prelen + len(icon) + 6

            else:
                icon = None

            script = script[prelen:]

        return script, dangerous


    def __make_preview__ (self, lines, preview_len = 0):
        if preview_len == 0:
            preview_len = self.preview_len

        if len (lines) > preview_len:
            result = lines[0:preview_len]
        else:
            result = lines

        result = result.replace("\n",";")
        result = result.replace ("&", "&amp;")
        #remove ending newlines, not if result len = 0
        result = result.strip ()

        if len(result) >= preview_len :
            result = result + "..."

        return result

