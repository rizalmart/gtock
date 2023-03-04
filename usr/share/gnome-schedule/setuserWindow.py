# setuserWindow.py - UI code for changing user
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

#python modules
import pwd


class SetuserWindow:
    def __init__(self, parent):
        self.ParentClass = parent
        self.builder = self.ParentClass.builder
        
        self.window = self.builder.get_object("setuserWindow")
        self.window.connect("delete-event", self.on_close_button_clicked)

        ##comboxEntry
        self.entUser = self.builder.get_object("entUser")

        liststore = Gtk.ListStore(GObject.TYPE_STRING)
        self.entUser.set_model(liststore)
        self.entUser.set_entry_text_column(0)

        #entryCompletion
        # TODO: make it only possible for the user to type something that is in the list
        self.entry = self.entUser.get_child()
        self.entry.set_text(self.ParentClass.user)
        completion = Gtk.EntryCompletion()
        self.entry.set_completion(completion)
        completion.set_model(liststore)
        completion.set_text_column(0)

        #fill combox with all the users
        pwd_info = pwd.getpwall()

        #self.entUser = Gtk.ComboBox.new_with_entry()
        
        liststore = Gtk.ListStore(str)

        for info in pwd_info:
            #print(info[0])
            liststore.append([info[0]]) 
            #self.entUser.append(info[0])
        ##
        
        self.entUser.set_model(liststore)

        self.cancel_button = self.builder.get_object("setuser_cancel_button")
        self.ok_button = self.builder.get_object("setuser_ok_button")
        self.cancel_button.connect("clicked", self.on_cancel_button_clicked)
        self.ok_button.connect("clicked", self.on_ok_button_clicked)


    #public function
    def ShowSetuserWindow (self):
        self.window.set_transient_for(self.ParentClass.window)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show_all()


    def on_cancel_button_clicked (self, *args):
        self.window.hide()


    def on_ok_button_clicked (self, *args):

        user = self.entry.get_text()
        try:
            self.ParentClass.changeUser(user)
            self.window.hide()

        except Exception as ex:
            print(ex)
            self.dialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _("No such user"))
            self.dialog.run ()
            self.dialog.destroy ()
	
    def on_close_button_clicked(self, widget, event):
        self.window.hide()
        return True
