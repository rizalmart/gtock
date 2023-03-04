# gnome-schedule-import-py - This import crontab and at tasks and installs
# them for the current user from the file specified.
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

sys.stderr.write(_("Gnome Schedule: Import tasks") + "\n")
if ("-h" in sys.argv) or ("--help" in sys.argv):
  sys.stderr.write(_("Usage: %s [input file]" % sys.argv[0]) + "\n")
  sys.stderr.write(_("       No file means import from stdin.") + "\n\n")
  sys.exit(0)

# Check file
if outf != False:
  if not os.access (outf, os.F_OK):
    sys.stderr.write (_("File does not exist.") + "\n")
    sys.exit (1)

if stdo:
  of = sys.stdin
  sys.stderr.write (_("Reading from stdin..") + "\n")
else:
  try:
    of = open(outf, 'rb')
    # Reading file
    sys.stderr.write (_("Reading file: %s.." % outf) + "\n")
  except:
    sys.stderr.write (_("Could not open file for reading: %s" % outf) + "\n")
    sys.exit (1)


d = pickle.load (of)

c = crontab.Crontab (is_root, user, uid, gid, home_dir)
c.read (easy = False)

crontabc = 0
for task in d.crontab:
  sys.stderr.write(_("Importing crontab task: %s" % task[0]) + "\n")
  (minute, hour, dom, moy, dow, command) = c.parse (task[3], True)
  c.append (minute, hour, dom, moy, dow, command, task[4], task[0])
  crontabc = crontabc + 1


# AT
a = at.At(is_root, user, uid, gid, home_dir, manual_poscorrect)
a.read ()

atc = 0
for task in d.at:
  sys.stderr.write(_("Importing at task: %s" % task[0]) + "\n")
  a.append (task[2] + " " + task[1], task[4], task[0], task[5])
  atc = atc + 1

sys.stderr.write (gettext.ngettext("Finished, imported: %d task total.",
                                   "Finished, imported: %d tasks total.",
                                   atc + crontabc) % (atc + crontabc) + "\n")

