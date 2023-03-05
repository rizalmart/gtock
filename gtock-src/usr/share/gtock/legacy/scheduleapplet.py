# scheduleapplet.py: contains code for the gnome-schedule applet
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>
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

poscorrect_isset = os.getenv ("POSIXLY_CORRECT", False)
manual_poscorrect = False
if poscorrect_isset == False:
    os.environ["POSIXLY_CORRECT"] = "enabled"
    manual_poscorrect = True

##
## I18N
##
import gettext
import locale
gettext.install(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR(), unicode=1)

if __name__ == "__main__":
    signal.signal (signal.SIGINT, signal.SIG_DFL)

debug_flag = None
if '--debug' in sys.argv:
    debug_flag = 1

try:
    import gi
    #tell pyGTK, if possible, that we want GTKv2
    gi.require_version("Gtk", "3.0")

except:
  #Some distributions come with GTK2, but not pyGTK
  pass

try:
  from gi.repository import Gtk
  import Gtk.glade
  # TODO: Gnome specific
  import gnomeapplet
  from gi.repository import GObject

except:
  print("You need to install pyGTK or GTKv2,\n"
          "or set your PYTHONPATH correctly.\n"
          "try: export PYTHONPATH= ")
  sys.exit(1)



class ScheduleApplet(gnomeapplet.Applet):
    def __init__(self, applet, iid, debug_flag, manual_poscorrect):
        self.__gobject_init__()
        self.debug_flag = debug_flag
        self.manual_poscorrect = manual_poscorrect

        gettext.bindtextdomain(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR())
        gettext.textdomain(config.GETTEXT_PACKAGE())

        locale.bindtextdomain(config.GETTEXT_PACKAGE(), config.GNOMELOCALEDIR())
        locale.textdomain(config.GETTEXT_PACKAGE())


        self.applet = applet
        self.__loadIcon__()


        self.ev_box = Gtk.EventBox()

        self.image = Gtk.Image()
        self.image.set_from_pixbuf(self.iconPixbuf)

        self.main_loaded = False

        self.ev_box.add(self.image)
        self.ev_box.show()
        self.ev_box.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.ev_box.connect("button_press_event", self.event_box_clicked)
        self.applet.add(self.ev_box)

        self.create_menu()
        self.applet.show_all()




    def __loadIcon__(self):
        if self.debug_flag:
            if os.access("../icons/gnome-schedule.svg", os.F_OK):
                self.iconPixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size ("../icons/gnome-schedule.svg", 18, 18)
        else:
            try:
                self.iconPixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size (config.getImagedir() + "/gnome-schedule.svg", 24, 24)
            except:
                print("ERROR: Could not load icon")

    def create_menu(self):
        self.verbs =    [       ("show_main", self.show_main_window),
                        ("add", self.add_task),
                        ("help", self.show_help),
                        ("about", self.show_about)
                ]

        #check for file in current dir
        if self.debug_flag:
            if os.access ("gnome-schedule-applet.xml", os.F_OK):
                datadir = './'
        else:
            if os.access (config.getGladedir() + "/gnome-schedule-applet.xml", os.F_OK):
                datadir = config.getGladedir()
            else:
                print("ERROR: Could not load menu xml file")
                datadir = ''
                quit ()

        self.applet.setup_menu_from_file(datadir,  "gnome-schedule-applet.xml", "gnome-schedule", self.verbs)


    def event_box_clicked (self, widget, event):
        if event.type == Gdk._2BUTTON_PRESS:
            self.show_main_window()

    def show_main_window(self, *args):
        if self.main_loaded == False:
            self.main_loaded = True
            self.main_window = mainWindow.main(None, True, self.manual_poscorrect)
        else:
            self.main_window.widget.show ()
            self.main_window.schedule_reload()


    def add_task(self, *args):
        if self.main_loaded == False:
            self.show_main_window()
            self.main_window.widget.hide()
        self.main_window.on_add_scheduled_task_menu_activate()


    def show_help(self, *args):
        if self.main_loaded == False:
            self.show_main_window()
            self.main_window.widget.hide()
        self.main_window.on_manual_menu_activate()

    def show_about(self, *args):
        if self.main_loaded == False:
            self.show_main_window()
            self.main_window.widget.hide()
        self.main_window.on_about_menu_activate()

GObject.type_register(ScheduleApplet)

#factory
def schedule_applet_factory(applet, iid):
    ScheduleApplet(applet, iid, debug_flag, manual_poscorrect)
    return True

gnomeapplet.bonobo_factory("OAFIID:GNOME_GnomeSchedule_Factory",
                                ScheduleApplet.__gtype__,
                                "GnomeScheduleApplet", "0", schedule_applet_factory)
