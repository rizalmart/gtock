# setcmdWindow.py - UI code for changing cmd
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

#pygtk modules
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gio

#python modules
import pwd


class SetcmdWindow:
    def __init__(self, parent):
		
        self.ParentClass = parent
        self.builder = self.ParentClass.builder
        
        self.settings = parent.settings
        
        self.window = self.builder.get_object("setcmdWindow")
        self.window.connect("delete-event", self.on_close_button_clicked)

        ##comboxEntry
        self.entCmd = self.builder.get_object("entCmd")

        
        
        self.entCmd.set_text(self.settings.get_string("terminal-exec"))

        
        self.cancel_button = self.builder.get_object("setcmd_cancel_button")
        self.ok_button = self.builder.get_object("setcmd_ok_button")
        self.cancel_button.connect("clicked", self.on_cancel_button_clicked)
        self.ok_button.connect("clicked", self.on_ok_button_clicked)


    #public function
    def ShowSetcmdWindow (self):
        self.window.set_transient_for(self.ParentClass.window)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show_all()


    def on_cancel_button_clicked (self, *args):
        self.window.hide()


    def on_ok_button_clicked (self, *args):

        cmd = self.entCmd.get_text()
        
        try:
                        
            self.settings.set_string("terminal-exec", cmd)
            
            self.window.hide()

        except Exception as ex:
            print(ex)
            self.dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _("No such terminal"))
            self.dialog.run ()
            self.dialog.destroy ()
	
    def on_close_button_clicked(self, widget, event):
        self.window.hide()
        return True
