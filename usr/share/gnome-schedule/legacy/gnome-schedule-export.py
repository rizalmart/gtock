# gnome-schedule-export-py - This exports crontab and at tasks with their info
# to the file specified.
#
# Copyright (C) 2011  Gaute Hope <eg at gaute dot vetsj dot com>
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

#python
import sys
import os
import pwd
import pickle

# g-s modules
import config
import crontab
import at
from db import *

# NEEDED FOR SUBMODULES
##
## I18N
##
import gettext
gettext.install(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR(), unicode=1)

poscorrect_isset = os.getenv ("POSIXLY_CORRECT", False)
manual_poscorrect = False
if poscorrect_isset == False:
    os.environ["POSIXLY_CORRECT"] = "enabled"
    manual_poscorrect = True

sys.stderr.write(_("Gnome Schedule: Export tasks") + "\n")
if ("-h" in sys.argv) or ("--help" in sys.argv):
  sys.stderr.write(_("Usage: %s [output file]" % sys.argv[0]) + "\n")
  sys.stderr.write(_("       No file means export to stdout.") + "\n\n")
  sys.exit(0)


# Parse arguments
if len(sys.argv) == 2:
  outf = sys.argv[1]
  stdo = False
else:
  outf = False
  stdo = True


uid = os.geteuid ()
gid = os.getegid ()
user = pwd.getpwuid (uid)[0]
home_dir = pwd.getpwuid (uid)[5]
user_shell = pwd.getpwuid (uid)[6]
if uid == 0: is_root = True
else: is_root = False

# Check file
if outf != False:
  if os.access (outf, os.F_OK):
    sys.stderr.write (_("File exists already.") + "\n")
    sys.exit (1)

if stdo:
  of = sys.stdout
else:
  try:
    of = open(outf, 'wb')
  except:
    sys.stderr.write (_("Could not open file for writing: %s" % outf) + "\n")
    sys.exit (1)

d = GnomeScheduleDB ()

c = crontab.Crontab (is_root, user, uid, gid, home_dir)
tasks = c.read (easy = False)
crontabc = 0
cl = []
for task in tasks:
  sys.stderr.write(_("Exporting crontab task: %s" % task[0]) + "\n")
  crontabc = crontabc + 1
  cl.append([task[0], task[5], task[2], task[3], task[14]])

d.setcrontab (cl)

# AT
a = at.At(is_root, user, uid, gid, home_dir, manual_poscorrect)
tasks = a.read ()
atc = 0
al = []
for task in tasks:
  sys.stderr.write(_("Exporting at task: %s" % task[0]) + "\n")
  atc = atc + 1
  al.append([task[0], task[8], task[11], task[2], task[3], task[14]])

d.setat (al)

pickle.dump(d, of, -1)
of.flush ()
of.close ()

sys.stderr.write(gettext.ngettext("Finished, exported: %d task total.",
                                  "Finished, exported: %d tasks total.",
                                  atc + crontabc) % (atc + crontabc) + "\n")

