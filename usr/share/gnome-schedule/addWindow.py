# addWindow.py - UI code for changing user
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2008 Gaute Hope <eg at gaute dot vetsj dot com>
# Copyright (C) 2004, 2005  Kristof Vansant <de_lupus at pandora dot be>
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
import gettext
import locale

from locale import gettext as _

class AddWindow:
    def __init__(self, parent):
		
        self.ParentClass = parent
        self.transient = self.ParentClass.window
        self.builder = self.ParentClass.builder
        
        self.window = self.builder.get_object("addWindow")
        self.window.connect("focus-out-event", self.window.hide_on_delete)
        self.window.connect("delete-event", self.on_close_button_clicked) 
        self.window.connect("destroy", self.window.destroy)

        self.mode = 0
        
        self.cancel_button = self.builder.get_object("select_cancel_button")
        self.button_at = self.builder.get_object("button_at")
        self.button_crontab = self.builder.get_object("button_crontab")
        self.button_template = self.builder.get_object("button_templates")
        
        self.cancel_button.connect("clicked", self.on_cancel_button_clicked)
        self.button_at.connect("clicked", self.on_button_at_clicked)
        self.button_crontab.connect("clicked", self.on_button_crontab_clicked)
        self.button_template.connect("clicked", self.on_button_template_clicked)

        self.chbox = Gtk.HBox (False, 5)
        self.cicon = Gtk.Image ()
        self.cicon.set_from_pixbuf (self.ParentClass.bigiconcrontab)
        self.cicon.set_alignment (0, 0.5)
        self.chbox.pack_start (self.cicon, False, False, 5)
        self.clabel = Gtk.Label(label=_("A task that launches recurrently"))
        self.clabel.set_justify (Gtk.Justification.LEFT)
        self.clabel.set_alignment (0, 0.5)
        self.chbox.pack_start (self.clabel, True, True, 5)
        
        self.button_crontab.add (self.chbox)
        self.button_crontab.show_all()
        
        self.ahbox = Gtk.HBox (False, 5)
        self.aicon = Gtk.Image ()
        self.aicon.set_from_pixbuf (self.ParentClass.bigiconat)
        self.aicon.set_alignment (0, 0.5)
        self.ahbox.pack_start (self.aicon, False, False, 5)
        self.alabel = Gtk.Label(label=_("A task that launches one time"))
        self.alabel.set_justify (Gtk.Justification.LEFT)
        self.alabel.set_alignment (0, 0.5)
        self.ahbox.pack_start (self.alabel, True, True, 5)
        
        self.button_at.add (self.ahbox)
        self.button_at.show_all ()
        
        self.thbox = Gtk.HBox(False, 5)
        self.ticon = Gtk.Image ()
        self.ticon.set_from_pixbuf(self.ParentClass.bigicontemplate)
        self.ticon.set_alignment (0, 0.5)
        self.thbox.pack_start (self.ticon, False, False, 5)
        self.tlabel = Gtk.Label(label=_("A task from a predefined template"))
        self.tlabel.set_justify (Gtk.Justification.LEFT)
        self.tlabel.set_alignment (0, 0.5)
        self.thbox.pack_start (self.tlabel, True, True, 5)
        
        self.button_template.add(self.thbox)
        self.button_template.show_all()


    # mode: 0 = normal add, 1 = new template
    def ShowAddWindow (self, transient, mode = 0):
		
        self.mode = mode
        self.transient = transient
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show_all()
        
        if (mode == 1):
            self.button_template.hide()
        elif (mode == 0):
            self.button_template.show_all()
        

    def on_cancel_button_clicked (self, *args):
        self.window.hide()
        
    def on_button_template_clicked (self, *args):
        self.ParentClass.template_chooser.show (self.transient)
        self.window.hide()
                
    def on_button_crontab_clicked (self, *args):
        self.ParentClass.editor = self.ParentClass.crontab_editor
        if (self.mode == 1):
            self.ParentClass.editor.shownew_template (self.transient)
        elif (self.mode == 0):
            self.ParentClass.editor.showadd(self.transient)
        self.window.hide()
        
    def on_button_at_clicked (self, *args):
        
        self.ParentClass.editor = self.ParentClass.at_editor
        
        if (self.mode == 1):
            self.ParentClass.editor.shownew_template(self.transient)
        elif (self.mode == 0):
            self.ParentClass.editor.showadd(self.transient)
        
        self.window.hide()
    
    def on_close_button_clicked(self, widget, event):
        self.window.hide()
        return True
        
