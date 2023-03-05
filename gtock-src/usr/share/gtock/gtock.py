#!/usr/bin/python3
# gtock.py - Starts up gtock
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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#python modules
import sys
import signal
import os

#custom modules
import config
import mainWindow


##
## I18N
##
import gettext
import locale

from locale import gettext as _

locale.bindtextdomain(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR())
locale.textdomain(config.GETTEXT_PACKAGE())


poscorrect_isset = os.getenv ("POSIXLY_CORRECT", False)
manual_poscorrect = False
if poscorrect_isset == False:
    os.environ['POSIXLY_CORRECT'] = 'enabled'
    manual_poscorrect = True

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)

debug_flag = None
if '--debug' in sys.argv:
    debug_flag = 1

try:
    import gi
    gi.require_version("Gtk", config.getGtkVersion())

except:
  pass

try:
  from gi.repository import Gtk
  #import Gtk.glade

except:
  print(_("You need to install pyGObject,\n"
          "or set your PYTHONPATH correctly.\n"
          "try: export PYTHONPATH= "))
  sys.exit(1)
  
if os.path.exists(config.getAtbin())==False and os.path.exists(config.getCrontabbin())==False:
    dialog = Gtk.MessageDialog(parent=None, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text="Please install CRON or AT")
    dialog.run()
    dialog.destroy()
    sys.exit(1)
else:
    mainWindow = mainWindow.main(debug_flag, False, manual_poscorrect)

