# crontabEditor.py - UI code for adding a crontab record
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot eu dot com>
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


#import gi
#gi.require_version('Gtk', '4.0')

from gi.repository import Gtk
from gi.repository import GObject

#python modules
import re
import os

#custom modules
import config
import crontabEditorHelper
import gettext
import locale

from locale import gettext as _



class CrontabEditor:
    def __init__(self, parent, backend, scheduler, template):

        self.ParentClass = parent
        self.backend = backend
        self.scheduler = scheduler
        self.template = template
        
        self.active_id=""

        self.builder = self.ParentClass.builder
        self.window = self.builder.get_object("crontab_editor")
        self.window.connect("delete-event", self.on_close_button_clicked)


        # TODO: move to crontab?
        self.fieldRegex = re.compile('^(\*)$|^([0-9]+)$|^\*\/([0-9]+)$|^([0-9]+)-([0-9]+)$|(^([0-9]+[,])+([0-9]+)$)')
        self.nooutputRegex = re.compile('([^#\n$]*)>(\s|)/dev/null\s2>&1')


        self.title_box = self.builder.get_object("crontab_title_box")

        self.image_icon = Gtk.Image ()
        self.image_icon.set_from_pixbuf (self.ParentClass.bigiconcrontab)
        self.title_box.pack_start (self.image_icon, False, False, 0)
        self.title_box.reorder_child (self.image_icon, 0)
        self.image_icon.show ()

        self.noevents = False


        ##simple tab
        self.entry_title = self.builder.get_object("entry_title")
        self.entry_task = self.builder.get_object("entry_task")

        self.frequency_combobox = self.builder.get_object("frequency_combobox")
        
        self.frequency_combobox_model = Gtk.ListStore (GObject.TYPE_STRING, GObject.TYPE_STRV)
        
        keylist=[
        (_("Every minute"), ["*", "*", "*", "*", "*", ""]),
        (_("Every hour"), ["0", "*", "*", "*", "*", ""]),
        (_("Every day"), ["0", "0", "*", "*", "*", ""]),
        (_("Every month"), ["0", "0", "1", "*", "*", ""]),
        (_("Every week"), ["0", "0", "*", "*", "1", ""]),
        (_("At reboot"), ["", "", "", "", "", "@reboot"])
        ]
        
        
        for key, value in keylist:
          self.frequency_combobox_model.append([key, value])
        
        self.frequency_combobox.set_model(self.frequency_combobox_model)
        
        cell = Gtk.CellRendererText()
        self.frequency_combobox.pack_start (cell, True)
        self.frequency_combobox.add_attribute (cell, "text", 0)
        
        self.cb_output = self.builder.get_object("combo_output")
        self.cb_o_model = Gtk.ListStore (GObject.TYPE_STRING, GObject.TYPE_INT)
        self.cb_o_model.append ([self.ParentClass.output_strings[0], 0])
        self.cb_o_model.append ([self.ParentClass.output_strings[1], 1])
        self.cb_o_model.append ([self.ParentClass.output_strings[2], 2])
        self.cb_o_model.append ([self.ParentClass.output_strings[3], 3])
        self.cb_output.set_model (self.cb_o_model)
        cell = Gtk.CellRendererText ()
        self.cb_output.pack_start (cell, True)
        self.cb_output.add_attribute (cell, "text", 0)

        self.button_cancel = self.builder.get_object("button_cancel")
        self.button_apply = self.builder.get_object("button_apply")
        self.button_template = self.builder.get_object("button_template")
        self.rb_advanced = self.builder.get_object("rb_advanced")
        self.rb_basic = self.builder.get_object("rb_basic")

        self.label_preview = self.builder.get_object("label_preview")

        self.button_cancel.connect("clicked", self.on_button_cancel_clicked)
        self.button_apply.connect("clicked", self.on_button_apply_clicked)

        self.entry_task.connect("changed", self.on_anybasic_entry_changed)
        self.frequency_combobox.connect("changed", self.on_frequency_combobox_changed)
        self.cb_output.connect ("changed", self.on_anybasic_entry_changed)

        self.rb_advanced.connect("toggled", self.on_editmode_toggled)
        self.rb_basic.connect("toggled", self.on_editmode_toggled)

        self.button_template.connect ("clicked", self.on_template_clicked)

        ##advanced
        self.minute_entry = self.builder.get_object("minute_entry")
        self.hour_entry = self.builder.get_object("hour_entry")
        self.day_entry = self.builder.get_object("day_entry")
        self.month_entry = self.builder.get_object("month_entry")
        self.weekday_entry = self.builder.get_object("weekday_entry")
        
        self.minute_entry.connect("changed", self.on_anyadvanced_entry_changed)
        self.hour_entry.connect("changed", self.on_anyadvanced_entry_changed)
        self.day_entry.connect("changed", self.on_anyadvanced_entry_changed)
        self.month_entry.connect("changed", self.on_anyadvanced_entry_changed)
        self.weekday_entry.connect("changed", self.on_anyadvanced_entry_changed)
		
        self.help_minute = self.builder.get_object("help_minute")
        self.help_hour = self.builder.get_object("help_hour")
        self.help_day = self.builder.get_object("help_day")
        self.help_month = self.builder.get_object("help_month")
        self.help_weekday = self.builder.get_object("help_weekday")

        self.help_minute.connect("clicked", self.on_fieldHelp_clicked)
        self.help_hour.connect("clicked", self.on_fieldHelp_clicked)
        self.help_day.connect("clicked", self.on_fieldHelp_clicked)
        self.help_month.connect("clicked", self.on_fieldHelp_clicked)
        self.help_weekday.connect("clicked", self.on_fieldHelp_clicked)
        

        self.editorhelper = crontabEditorHelper.CrontabEditorHelper(self)



    def showadd (self, transient):
        self.button_apply.set_label (Gtk.STOCK_ADD)
        self.__reset__ ()
        self.mode = 0
        self.window.set_title(_("Create a New Scheduled Task"))
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.button_template.show ()
        self.window.show ()
        self.cb_output.set_active (0)

    def showadd_template (self, transient, title, command, output,timeexpression):
        self.button_apply.set_label (Gtk.STOCK_ADD)
        self.__reset__ ()
        self.mode = 0
        self.window.set_title(_("Create a New Scheduled Task"))
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.button_template.show ()
        self.window.show ()

        self.output = output
        # hehe again, why make it less complicated..
        timeexpression = timeexpression + " echo hehe"
        self.minute, self.hour, self.day, self.month, self.weekday, hehe = self.scheduler.parse (timeexpression, True)
        self.special = ""
        if self.minute == "@reboot":
            self.special = "@reboot"
            self.minute = ""
            self.day = ""
            self.hour = ""
            self.month = ""
            self.weekday = ""
        self.command = command
        self.title = title

        self.__update_textboxes__ ()

        i = self.__getfrequency__ (self.minute, self.hour, self.day, self.month, self.weekday, self.special)
        if i == -1:
            # advanced
            self.rb_advanced.set_active (True)
        else:
            self.rb_basic.set_active (True)
            self.frequency_combobox.set_active(i)

        self.cb_output.set_active(int(self.output))


    def showedit_template (self, transient, id, title, command, output, timeexpression):
        self.button_apply.set_label (Gtk.STOCK_SAVE)

        self.mode = 2
        self.tid = id
        self.__reset__ ()

        self.command = command
        self.title = title
        self.output = output

        timeexpression = timeexpression + " echo hehe"
        self.minute, self.hour, self.day, self.month, self.weekday, hehe = self.scheduler.parse (timeexpression, True)
        self.special = ""
        if self.minute == "@reboot":
            self.special = "@reboot"
            self.minute = ""
            self.day = ""
            self.hour = ""
            self.month = ""
            self.weekday = ""

        self.window.set_title(_("Edit template"))
        self.__update_textboxes__ ()

        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show ()
        self.button_template.hide ()
        i = self.__getfrequency__ (self.minute, self.hour, self.day, self.month, self.weekday, self.special)
        if i == -1:
            # advanced
            self.rb_advanced.set_active (True)
        else:
            self.rb_basic.set_active (True)
            self.frequency_combobox.set_active(i)

        self.cb_output.set_active(int(self.output))
        
        self.ParentClass.template_manager.window.hide()

    def shownew_template (self, transient):
        self.button_apply.set_label (Gtk.STOCK_ADD)

        self.mode = 2
        self.tid = 0
        self.__reset__ ()


        self.window.set_title(_("New template"))
        self.__update_textboxes__ ()

        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show ()
        self.button_template.hide ()
        self.ParentClass.template_manager.window.hide()


    def showedit (self, transient, record, job_id, linenumber, iter):
        self.button_apply.set_label (Gtk.STOCK_APPLY)
        self.mode = 1
        self.linenumber = linenumber
        self.record = record
        self.job_id = job_id
        self.__reset__ ()
        (self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.comment, self.job_id, self.title, self.desc, self.output, display) = self.scheduler.parse (record)[1]
        self.special = ""
        if self.minute == "@reboot":
            self.special = "@reboot"
            self.minute = ""
            self.day = ""
            self.hour = ""
            self.month = ""
            self.weekday = ""

        self.window.set_title(_("Edit a Scheduled Task"))
        self.__update_textboxes__ ()
        self.parentiter = iter
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.button_template.show ()
        self.window.show ()
        i = self.__getfrequency__ (self.minute, self.hour, self.day, self.month, self.weekday, self.special)
        if i == -1:
            # advanced
            self.rb_advanced.set_active (True)
        else:
            self.rb_basic.set_active (True)
            self.frequency_combobox.set_active (i)

        self.cb_output.set_active (self.output)

    def __reset__ (self):
        self.noevents = True
        self.minute = "0"
        self.hour = "*"
        self.day = "*"
        self.month = "*"
        self.weekday = "*"
        self.special = ""
        self.command = "ls"
        self.title = _("Untitled")
        self.output = 0
        self.frequency_combobox.set_active (1)
        self.rb_basic.set_active (True)
        self.minute_entry.set_editable (False)
        self.minute_entry.set_sensitive (False)
        self.hour_entry.set_editable (False)
        self.hour_entry.set_sensitive (False)
        self.day_entry.set_editable (False)
        self.day_entry.set_sensitive (False)
        self.month_entry.set_editable (False)
        self.month_entry.set_sensitive (False)
        self.weekday_entry.set_editable (False)
        self.weekday_entry.set_sensitive (False)
        self.help_minute.set_sensitive (False)
        self.help_hour.set_sensitive (False)
        self.help_day.set_sensitive (False)
        self.help_month.set_sensitive (False)
        self.help_weekday.set_sensitive (False)
        self.cb_output.set_active (0)
        self.frequency_combobox.set_sensitive(True)
        self.__update_textboxes__ ()
        self.noevents = False


    #error dialog box
    def __WrongRecordDialog__ (self, x, y, z):
        self.wrongdialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, (_("This is an invalid record! The problem could be in the %(field)s field. Reason: %(reason)s") % (y, z)))
        self.wrongdialog.run()
        self.wrongdialog.destroy()

    def __dialog_command_failed__ (self):
        self.wrongdialog2 = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, (_("Your command contains one or more of the character %, this is special for cron and cannot be used with gtock because of the format it uses to store extra information on the crontab line. Please use the | redirector character to achieve the same functionality. Refer to the crontab manual for more information about the % character. If you don not want to use it for redirection it must be properly escaped with the \ letter.")))
        self.wrongdialog2.run()
        self.wrongdialog2.destroy()

    def __check_field_format__ (self, field, type):
        try:
            # Type should not be translatable!
            self.scheduler.checkfield (field, type)
        except Exception as ex:
            raise ex

    def on_editmode_toggled (self, widget, *args):
        if widget.get_active() == True:
            if self.noevents == False:
                self.noevents = True
                if widget.get_name() == self.rb_advanced.get_name():
                    self.rb_basic.set_active (False)
                    if (self.frequency_combobox.get_active () == 5):
                        # reboot, standard every hour
                        self.special = ""
                        self.minute_entry.set_text ("0")
                        self.hour_entry.set_text ("*")
                        self.day_entry.set_text ("*")
                        self.month_entry.set_text ("*")
                        self.weekday_entry.set_text ("*")
                        self.minute = "0"
                        self.hour = "*"
                        self.day = "*"
                        self.month = "*"
                        self.weekday = "*"

                        self.update_preview ()

                    self.rb_advanced.set_active (True)
                    self.minute_entry.set_editable (True)
                    self.minute_entry.set_sensitive (True)
                    self.hour_entry.set_editable (True)
                    self.hour_entry.set_sensitive (True)
                    self.day_entry.set_editable (True)
                    self.day_entry.set_sensitive (True)
                    self.month_entry.set_editable (True)
                    self.month_entry.set_sensitive (True)
                    self.weekday_entry.set_editable (True)
                    self.weekday_entry.set_sensitive (True)
                    self.help_minute.set_sensitive (True)
                    self.help_hour.set_sensitive (True)
                    self.help_day.set_sensitive (True)
                    self.help_month.set_sensitive (True)
                    self.help_weekday.set_sensitive (True)
                    self.frequency_combobox.set_sensitive (False)
                else:
                    self.rb_basic.set_active (True)
                    self.rb_advanced.set_active (False)
                    self.minute_entry.set_editable (False)
                    self.minute_entry.set_sensitive (False)
                    self.hour_entry.set_editable (False)
                    self.hour_entry.set_sensitive (False)
                    self.day_entry.set_editable (False)
                    self.day_entry.set_sensitive (False)
                    self.month_entry.set_editable (False)
                    self.month_entry.set_sensitive (False)
                    self.weekday_entry.set_editable (False)
                    self.weekday_entry.set_sensitive (False)
                    self.help_minute.set_sensitive (False)
                    self.help_hour.set_sensitive (False)
                    self.help_day.set_sensitive (False)
                    self.help_month.set_sensitive (False)
                    self.help_weekday.set_sensitive (False)
                    self.frequency_combobox.set_sensitive (True)
                    self.on_frequency_combobox_changed (self.frequency_combobox)
                self.noevents = False


    def on_button_cancel_clicked (self, *args):
        self.window.hide()
        
        if self.mode==2:
         self.ParentClass.template_manager.window.show()

    def on_template_clicked (self, *args):
        if self.special != "":
            try:
                self.__check_field_format__ (self.special, "special")
                record = self.special + " " + self.command
                self.minute = "@reboot"
                self.hour = "@reboot"
                self.day = "@reboot"
                self.month = "@reboot"
                self.weekday = "@reboot"
            except Exception as ex:
                x, y, z = ex
                self.__WrongRecordDialog__ (x, y, z)
                return
        else:
            try:
                # Type should not be translatable!
                self.__check_field_format__ (self.minute, "minute")
                self.__check_field_format__ (self.hour, "hour")
                self.__check_field_format__ (self.day, "day")
                self.__check_field_format__ (self.month, "month")
                self.__check_field_format__ (self.weekday, "weekday")
                record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command
            except Exception as ex:
                x, y, z = ex
                self.__WrongRecordDialog__ (x, y, z)
                return

        if self.scheduler.check_command (self.command) == False:
            self.__dialog_command_failed__ ()
            return  False

        if self.special != "":
            self.template.savetemplate_crontab (0, self.title, self.command, self.output, self.special)
        else:
            self.template.savetemplate_crontab (0, self.title, self.command, self.output, self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday)

        self.window.hide ()

    def on_button_apply_clicked (self, *args):
        if self.special != "":
            try:
                self.__check_field_format__ (self.special, "special")
                record = self.special + " " + self.command
                self.minute = "@reboot"
                self.hour = "@reboot"
                self.day = "@reboot"
                self.month = "@reboot"
                self.weekday = "@reboot"
            except Exception as ex:
                x, y, z = ex
                self.__WrongRecordDialog__ (x, y, z)
                return
        else:
            try:
                # Type should not be translatable!
                self.__check_field_format__ (self.minute, "minute")
                self.__check_field_format__ (self.hour, "hour")
                self.__check_field_format__ (self.day, "day")
                self.__check_field_format__ (self.month, "month")
                self.__check_field_format__ (self.weekday, "weekday")
                record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command
            except Exception as ex:
                x, y, z = ex
                self.__WrongRecordDialog__ (x, y, z)
                return

        if self.scheduler.check_command (self.command) == False:
            self.__dialog_command_failed__ ()
            return  False


        if (self.backend.get_not_inform_working_dir_crontab() != True):
            dia2 = Gtk.MessageDialog (self.window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.WARNING, Gtk.ButtonsType.NONE, _("Note about working directory of executed tasks:\n\nRecurrent tasks will be run from the home directory."))
            dia2.add_buttons (_("_Don't show again"), Gtk.ResponseType.CLOSE, Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            dia2.set_title (_("Warning: Working directory of executed tasks"))
            response = dia2.run ()
            if response == Gtk.ResponseType.CANCEL:
                dia2.destroy ()
                del dia2
                return
            elif response == Gtk.ResponseType.CLOSE:
                self.backend.set_not_inform_working_dir_crontab (True)
            else:
                pass
            dia2.destroy ()
            del dia2

        self.title=self.entry_title.get_text()

        if self.mode == 1:
            self.scheduler.update (self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.linenumber, self.parentiter, self.output, self.job_id, self.comment, self.title, self.desc)

        elif self.mode == 0:
            #print("append")
            self.scheduler.append (self.minute, self.hour, self.day, self.month, self.weekday, self.command, self.output, self.title)
            
        elif self.mode == 2:
            if self.special != "":
                try:
                    self.__check_field_format__ (self.special, "special")
                    record = self.special + " " + self.command
                    self.minute = "@reboot"
                    self.hour = "@reboot"
                    self.day = "@reboot"
                    self.month = "@reboot"
                    self.weekday = "@reboot"
                except Exception as ex:
                    x, y, z = ex
                    self.__WrongRecordDialog__ (x, y, z)
                    return
            else:
                try:
                    # Type should not be translatable!
                    self.__check_field_format__ (self.minute, "minute")
                    self.__check_field_format__ (self.hour, "hour")
                    self.__check_field_format__ (self.day, "day")
                    self.__check_field_format__ (self.month, "month")
                    self.__check_field_format__ (self.weekday, "weekday")
                    record = self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday + " " + self.command
                except Exception as ex:
                    x, y, z = ex
                    self.__WrongRecordDialog__ (x, y, z)
                    return

            if self.scheduler.check_command (self.command) == False:
                self.__dialog_command_failed__ ()
                return  False

            if self.special != "":
                self.template.savetemplate_crontab (self.tid, self.title, self.command, self.output, self.special)
            else:
                self.template.savetemplate_crontab (self.tid, self.title, self.command, self.output, self.minute + " " + self.hour + " " + self.day + " " + self.month + " " + self.weekday)

            self.window.hide ()
            self.ParentClass.template_manager.reload_tv()
            
            return

        self.ParentClass.schedule_reload()
        
        if self.mode == 2:
          self.ParentClass.template_manager.window.show()		
        
        self.window.hide()	


    def __set_frequency_combo__ (self):
        if self.noevents == False:
            index = self.__getfrequency__ (self.minute, self.hour, self.day, self.month, self.weekday, self.special)
            if index != -1:
                self.frequency_combobox.set_active(index)
            else:
                self.rb_advanced.set_active(True)


    def __getfrequency__ (self, minute, hour, day, month, weekday, special):
        index = -1

        if minute == "*" and hour == "*" and month == "*" and day == "*" and weekday == "*":
            index = 0
        if minute == "0" and hour == "*" and month == "*" and day == "*" and weekday == "*":
            index = 1
        if minute == "0" and hour == "0" and month == "*" and day == "*" and weekday == "*":
            index = 2
        if minute == "0" and hour == "0" and month == "*" and day == "1" and weekday == "*":
            index = 3
        if minute == "0" and hour == "0" and month == "*" and day == "*" and weekday == "1":
            index = 4
        if special != "":
            index = 5


        return index


    def __update_textboxes__ (self):
        self.noevents = True
        #self.cb_output.set_active(self.output)
        self.entry_task.set_text(self.command)
        self.entry_title.set_text(self.title)
        self.minute_entry.set_text(self.minute)
        self.hour_entry.set_text(self.hour)
        self.day_entry.set_text(self.day)
        self.month_entry.set_text(self.month)
        self.weekday_entry.set_text(self.weekday)
        self.update_preview ()
        #self.__set_frequency_combo__()
        self.noevents = False

    def update_preview (self):
        if self.special != "":
            try:
                self.__check_field_format__ (self.special, "special")
                record = self.special + " " + self.command
                minute = "@reboot"
                hour = "@reboot"
                day = "@reboot"
                month = "@reboot"
                weekday = "@reboot"
                self.label_preview.set_text ("<b>" + self.scheduler.__easy__ (minute, hour, day, month, weekday) + "</b>")

            except Exception as ex:
                x, y, z = ex
                self.label_preview.set_text (_("This is an invalid record! The problem could be in the %(field)s field. Reason: %(reason)s") % ({'field' : y, 'reason' : z}))


        else:
            try:
                # Type should not be translatable!
                self.__check_field_format__ (self.minute, "minute")
                self.__check_field_format__ (self.hour, "hour")
                self.__check_field_format__ (self.day, "day")
                self.__check_field_format__ (self.month, "month")
                self.__check_field_format__ (self.weekday, "weekday")

                # Day of Month
                # Crontab bug? Let's not support
                # dom behaves like minute
                """
                dom = self.day
                if dom.isdigit() == False:
                    dom = dom.lower ()
                    for day in self.scheduler.downumbers:
                        dom = dom.replace (day, self.scheduler.downumbers[day])
                """

                # Month of Year
                moy = self.month
                if moy.isdigit () == False:
                    moy = moy.lower ()
                    for m in self.scheduler.monthnumbers:
                        moy = moy.replace (m, self.scheduler.monthnumbers[m])


                # Day of Week
                dow = self.weekday
                if dow.isdigit() == False:
                    dow = dow.lower ()
                    for day in self.scheduler.downumbers:
                        dow = dow.replace (day, self.scheduler.downumbers[day])
                self.label_preview.set_text ("<b>" + self.scheduler.__easy__ (self.minute, self.hour, self.day, moy, dow) + "</b>")
            except Exception as ex:
                x=ex
                y=ex
                z=ex
                self.label_preview.set_text (_("This is an invalid record! The problem could be in the %(field)s field. Reason: %(reason)s") % ({'field' : y, 'reason' : z}))

        self.label_preview.set_use_markup (True)


    def on_anyadvanced_entry_changed (self, *args):
        if self.noevents == False:
            self.minute = self.minute_entry.get_text ()
            self.hour = self.hour_entry.get_text ()
            self.day = self.day_entry.get_text ()
            self.month = self.month_entry.get_text ()
            self.weekday = self.weekday_entry.get_text ()
            self.output = self.cb_output.get_active()

            self.__update_textboxes__ ()


    def on_anybasic_entry_changed (self, *args):
        if self.noevents == False:
            self.command = self.entry_task.get_text()
            self.title = self.entry_title.get_text()
            self.output = self.cb_output.get_active()
            self.__update_textboxes__ ()


    def on_frequency_combobox_changed(self, bin):
        iter = self.frequency_combobox.get_active_iter()
        frequency = self.frequency_combobox_model.get_value(iter, 1)
        if frequency != None:
            self.minute, self.hour, self.day, self.month, self.weekday, self.special = frequency
            self.__update_textboxes__()

    def on_fieldHelp_clicked(self, widget, *args):
		
        name = widget.get_name()
        print(">>" + name)
        field = "minute"
        expression = self.minute_entry.get_text()
        if name == "help_minute" :
            field = "minute"
            expression = self.minute_entry.get_text()
        if name == "help_hour" :
            field = "hour"
            expression = self.hour_entry.get_text()
        if name == "help_day" :
            field = "day"
            expression = self.day_entry.get_text()
        if name == "help_month" :
            field = "month"
            expression = self.month_entry.get_text()
        if name == "help_weekday" :
            field = "weekday"
            expression = self.weekday_entry.get_text()

        self.editorhelper.show(field, expression)

    def on_close_button_clicked(self, widget, event):
        self.window.hide()
        
        return True
