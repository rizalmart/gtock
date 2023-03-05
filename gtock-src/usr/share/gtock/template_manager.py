# template_manager.py: the template manager window
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
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


from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf

import gettext
import locale

from locale import gettext as _


class TemplateManager:
    def __init__ (self, parent, template):
        self.parent = parent
        self.template = template

        # setup window
        self.builder = self.parent.builder
        self.window = self.builder.get_object("template_manager")
        self.window.connect("delete-event", self.on_cancel_clicked)
        #self.window.connect("destroy", self.window.destroy)

        self.treeview = self.builder.get_object("tm_treeview")
        self.button_use = self.builder.get_object("tm_button_use")
        
        hbox = Gtk.HBox ()
        icon = Gtk.Image ()
        icon.set_from_pixbuf (self.parent.normalicontemplate)
        label = Gtk.Label(label=_("Use template"))
        icon.set_alignment (0.5, 0.5)
        label.set_justify (Gtk.Justification.CENTER)
        label.set_alignment (0.5, 0.5)
        hbox.pack_start (icon, True, True, 0)
        hbox.pack_start (label, True, True, 0)
        self.button_use.add (hbox)
        self.button_use.show_all ()

        self.button_cancel = self.builder.get_object("tm_button_cancel")
        self.button_new= self.builder.get_object("tm_button_new")
        self.button_edit = self.builder.get_object("tm_button_edit")
        self.button_delete = self.builder.get_object("tm_button_delete")
        

        self.button_new.connect ("clicked", self.on_new_clicked)
        self.button_use.connect ("clicked", self.on_use_clicked)
        self.button_cancel.connect ("clicked", self.on_cancel_clicked)
        self.button_edit.connect ("clicked", self.on_edit_clicked)
        self.button_delete.connect ("clicked", self.on_delete_clicked)
        self.treeview.connect ("button-press-event", self.on_tv_pressed)



        self.treeview.get_selection().connect("changed", self.on_tv_changed)

        # setup liststore
        # [template id, type, type-string, formatted text, icon/pixbuf]
        self.treemodel = Gtk.ListStore (GObject.TYPE_INT, GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING, GdkPixbuf.Pixbuf)

        # setup treeview
        self.treeview.set_model (self.treemodel)
        self.treeview.set_headers_visible (True)


        rend1 = Gtk.CellRendererPixbuf ()
        rend2 = Gtk.CellRendererText ()

        column = Gtk.TreeViewColumn(_("Task"))
        column.pack_start (rend1, True)
        column.pack_end (rend2, True)
        column.add_attribute (rend1, "pixbuf", 4)
        column.add_attribute (rend2, "text", 2)
        self.treeview.append_column(column)


        rend = Gtk.CellRendererText ()
        column = Gtk.TreeViewColumn(_("Description"), rend, markup=3)
        self.treeview.append_column(column)

    def on_tv_changed (self, *args):
        if self.treeview.get_selection().count_selected_rows() > 0 :
            value = True
        else:
            value = False
        self.button_use.set_sensitive (value)
        self.button_edit.set_sensitive (value)
        self.button_delete.set_sensitive (value)

    def reload_tv (self):
        self.treemodel.clear ()
        at = self.template.gettemplateids ("at")
        if at != None:
            for id in at:
                t = self.template.gettemplate ("at", int (id))
                if t != False:
                    id2, title, command, output = t
                    formatted = self.template.format_at (title, command, output)
                    iter = self.treemodel.append ([int (id), "at", _("One-time"), formatted, self.parent.bigiconat])

        crontab = self.template.gettemplateids ("crontab")
        if crontab != None:
            for id in crontab:
                t = self.template.gettemplate ("crontab", int (id))
                if t != False:
                    id2, title, command, output, timeexpression = t
                    formatted = self.template.format_crontab (title, command, output, timeexpression)
                    iter = self.treemodel.append ([int (id), "crontab", _("Recurrent"), formatted, self.parent.bigiconcrontab])

    def on_edit_clicked (self, *args):
        store, iter = self.treeview.get_selection().get_selected()
        if iter != None:
            type = self.treemodel.get_value(iter, 1)
            id = self.treemodel.get_value(iter, 0)
            if type == "at":
                t = self.template.gettemplate ("at", int (id))
                if t != False:
                    id2, title, command, output = t
                    self.parent.at_editor.showedit_template(self.window, id2, title, command, output)

            elif type == "crontab":
                t = self.template.gettemplate ("crontab", int (id)  )
                if t != False:
                    id2, title, command, output, timeexpression = t
                    self.parent.crontab_editor.showedit_template (self.window, id2, title, command, output, timeexpression)
        self.reload_tv ()

    def on_new_clicked (self, *args):
        self.parent.addWindow.ShowAddWindow(self.window,1)

    def on_delete_clicked (self, *args):
        store, iter = self.treeview.get_selection().get_selected()
        if iter != None:
            type = self.treemodel.get_value(iter, 1)
            id = self.treemodel.get_value(iter, 0)
            if type == "at":
                self.template.removetemplate_at (id)
            elif type == "crontab":
                self.template.removetemplate_crontab (id)

        self.reload_tv ()



    def show (self, transient):
        # populate treeview
        self.reload_tv ()

        #self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show_all ()

    def on_tv_pressed (self, widget, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.on_edit_clicked(self, widget)

    def on_use_clicked (self, *args):
        store, iter = self.treeview.get_selection().get_selected()
        if iter != None:
            type = self.treemodel.get_value(iter, 1)
            id = self.treemodel.get_value(iter, 0)
            if type == "at":
                t = self.template.gettemplate ("at", int (id))
                if t != False:
                    id2, title, command, output = t
                    self.parent.at_editor.showadd_template(self.window, title, command, output)
            elif type == "crontab":
                t = self.template.gettemplate ("crontab", int (id)  )
                if t != False:
                    id2, title, command, output, timeexpression = t
                    self.parent.crontab_editor.showadd_template(self.window, title, command, output, timeexpression)

            self.window.hide()

    def on_cancel_clicked (self, *args):
        self.window.hide ()
        return True




