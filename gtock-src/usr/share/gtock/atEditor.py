# atEditor.py - UI code for adding an at record
# Copyright (C) 2004, 2005  Philip Van Hoof <me at pvanhoof dot be>
# Copyright (C) 2004 - 2009 Gaute Hope <eg at gaute dot vetsj dot com>
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
from gi.repository import GObject

#python modules
import os
import re
import time
import calendar

#custom modules
import config
import gettext
import locale
import calendar

from locale import gettext as _



class AtEditor:
    def __init__(self, parent, backend, scheduler, template):
		
        self.ParentClass = parent
        self.builder = self.ParentClass.builder
        self.backend = backend
        self.scheduler = scheduler
        self.template = template
        self.hostclass=None

        # FreeBSD supports time ranges between 0 and 23:59
        if self.scheduler.sysname == 'FreeBSD':
          self.HOUR_MAX = 23
        else:
          self.HOUR_MAX = 24

        self.window = self.builder.get_object("at_editor")
        self.window.connect("delete-event", self.on_button_cancel_clicked)
        #self.window.connect("destroy", self.window.destroy)
        self.window.connect("event", self.on_at_editor_size_changed)
        self.window.connect("focus-out-event", self.__destroy_calendar__)

        self.mode = 0 # 0 = add, 1 = edit, 2 = template

        self.button_save = self.builder.get_object("at_button_save")
        self.button_cancel = self.builder.get_object("at_button_cancel")
        self.entry_title = self.builder.get_object("at_entry_title")
        self.text_task = self.builder.get_object("at_text_task")
        self.text_task_buffer = self.text_task.get_buffer()
        self.button_add_template = self.builder.get_object("at_button_template")
        self.at_vbox_time = self.builder.get_object("at_vbox_time")

        self.cb_xoutput = self.builder.get_object("cb_xoutput")

        self.spin_hour = self.builder.get_object("at_spin_hour")
        self.spin_minute = self.builder.get_object("at_spin_minute")
        self.spin_year = self.builder.get_object("at_spin_year")
        self.spin_month = self.builder.get_object("at_spin_month")
        self.spin_day = self.builder.get_object("at_spin_day")

        self.title_box = self.builder.get_object("title_box")

        self.image_icon = Gtk.Image ()
        self.image_icon.set_from_pixbuf(self.ParentClass.bigiconat)
        self.title_box.pack_start (self.image_icon, False, False, 0)
        self.title_box.reorder_child (self.image_icon, 0)
        self.image_icon.show ()

        self.cal_button = self.builder.get_object("cal_button")
        self.cal_hbox = Gtk.HBox ()
        self.calicon = Gtk.Image ()
        self.calicon.set_from_pixbuf (self.ParentClass.iconcalendar)
        self.arrow = Gtk.Arrow (Gtk.ArrowType.DOWN, Gtk.ShadowType.OUT)
        self.cal_label = Gtk.Label(label=_("Calendar"))
        self.cal_hbox.add (self.calicon)
        self.cal_hbox.add (self.cal_label)
        self.cal_hbox.add (self.arrow)
        self.cal_button.add (self.cal_hbox)
        self.cal_button.show_all ()

        self.cal_button.connect("toggled", self.on_cal_button_toggled)
        self.cal_button.connect("focus-out-event", self.__destroy_calendar__)
        
        
        self.cb_xoutput.connect("toggled", self.on_cb_xoutput_toggled)

        self.cal_loaded = False
        self.x, self.y = self.window.get_position()
        self.height, self.width = self.window.get_size()
        self.cal_active = True

        self.button_cancel.connect("clicked", self.on_button_cancel_clicked)
        self.button_save.connect("clicked", self.on_button_save_clicked)

        self.text_task.connect("popup-menu", self.on_text_task_popup_menu)
        self.text_task.connect("key-release-event", self.on_text_task_change)

        self.entry_title.connect("changed", self.on_entry_title_changed)

        self.button_add_template.connect("clicked", self.on_button_template_clicked)

        self.check_spin_running = False

        self.spin_hour.connect("changed", self.on_spin_hour_changed)
        self.spin_minute.connect("changed", self.on_spin_minute_changed)
        self.spin_year.connect("changed", self.on_spin_year_changed)
        self.spin_month.connect("changed", self.on_spin_month_changed)
        self.spin_day.connect("changed", self.on_spin_day_changed)

        ctime = time.localtime()
        year = ctime[0]
        month= ctime[1]
        day= ctime[2]
        
        #self.spin_year.set_range(year, year + 5847) # TODO: Year +5847 compatability
        
        
        self.spin_year.set_adjustment(Gtk.Adjustment(year, 1970, year + 5847, step_increment=1, page_increment=1, page_size=0))
        self.spin_month.set_adjustment(Gtk.Adjustment(month, 1, 12, step_increment=1, page_increment=1, page_size=0))
        
        if month == 2:
          if self.is_leap_year(year)==True:	
           end_day=29
          else:
           end_day=28   
        else:
           t1, end_day=calendar.monthrange(year, month)	

        self.spin_day.set_adjustment(Gtk.Adjustment(day, 1, end_day, step_increment=1, page_increment=1, page_size=0))
        
        self.spin_hour.set_adjustment(Gtk.Adjustment(month, 0, self.HOUR_MAX, step_increment=1, page_increment=1, page_size=0))
        
        self.spin_minute.set_adjustment(Gtk.Adjustment(month, 0, 59, step_increment=1, page_increment=1, page_size=0))

        
        self.timeout_handler_id = GObject.timeout_add(60 * 1000, self.__check_spins__)
        
    def is_leap_year(year):
      if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
      else:
        return False        

    def showadd (self, transient):
        self.button_save.set_label (Gtk.STOCK_ADD)
        self.__reset__ ()
        self.title = _("Untitled")
        self.mode = 0 # add new task
        self.window.set_title(_("Create a New Scheduled Task"))
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.__setup_calendar__ ()
        self.button_add_template.show()
        self.window.show_all()
        self.output = 0
        self.cb_xoutput.set_active(0)

        self.__update_textboxes__()

    def showadd_template (self, transient, title, command, output):
        self.button_save.set_label (Gtk.STOCK_ADD)
        self.__reset__ ()
        self.title = title
        self.command = command
        self.mode = 0 # add new task
        self.output = output
        self.window.set_title(_("Create a New Scheduled Task"))
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show()
        self.at_vbox_time.show()
        self.__setup_calendar__ ()
        self.button_add_template.show ()
        self.cb_xoutput.set_active (output)
        self.__update_textboxes__()

    def showedit_template (self, transient, id, title, command, output):
        self.button_save.set_label(Gtk.STOCK_ADD)
        self.__reset__ ()
        self.tid = id
        self.title = title
        self.command = command
        self.mode = 2 # edit template
        self.output = output
        self.cb_xoutput.set_active (output)
        self.window.set_title(_("Edit template"))
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.__setup_calendar__ ()
        self.window.show_all ()

        # hide time settings
        self.at_vbox_time.hide ()

        # save and cancel buttons
        self.button_save.set_label (Gtk.STOCK_SAVE)
        self.button_add_template.hide ()

        self.__update_textboxes__()
        
        transient.hide()

    def shownew_template (self, transient,):
		
        self.button_save.set_label (Gtk.STOCK_ADD)
        self.__reset__ ()
        self.tid = 0
        self.mode = 2 # edit template
        self.output = 0
        self.window.set_title(_("New template"))
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.show()
        
        self.cb_xoutput.set_active(0)
        self.__setup_calendar__ ()

        # hide time settings
        self.at_vbox_time.hide()

        # save and cancel buttons
        self.button_save.set_label (Gtk.STOCK_ADD)
        self.button_add_template.hide()

        self.__update_textboxes__()
        
        transient.hide()
        
        print("temp end")
        
    def showedit (self, transient, record, job_id, iter):
        self.button_save.set_label (Gtk.STOCK_APPLY)
        self.mode = 1 # edit task
        self.job_id = job_id
        self.date = self.ParentClass.treemodel.get_value(iter, 9)
        self.time = self.ParentClass.treemodel.get_value(iter, 12)
        self.title = self.ParentClass.treemodel.get_value(iter, 0)
        self.class_id = self.ParentClass.treemodel.get_value(iter, 10)
        self.user = self.ParentClass.treemodel.get_value(iter, 11)
        self.command = self.ParentClass.treemodel.get_value(iter, 3)
        self.output = self.ParentClass.treemodel.get_value (iter, 15)
        self.cb_xoutput.set_active (self.output)
        # removing beginning newlines.. wherever they come from..
        i = self.command.find ('\n', 0)
        while i == 0:
            self.command = self.command[1:]
            i = self.command.find ('\n', 0)

        #parse
        (hour, minute, day, month, year) = self.__parse_time__(self.time, self.date)
        self.runat = hour + minute  + " " + day + "." + month + "." + year
        self.spin_year.set_value (int (year))
        self.spin_month.set_value (int (month))
        self.spin_day.set_value (int (day))

        self.spin_hour.set_value(int(hour))
        self.spin_minute.set_value(int(minute))
        self.window.set_title(_("Edit a Scheduled Task"))

        self.__update_textboxes__()
        self.parentiter = iter
        self.window.set_transient_for(transient)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.__setup_calendar__ ()
        self.button_add_template.show()
        self.window.show_all()



    def on_cal_lost_focus (self, *args):
        self.__hide_calendar__ ()

    def on_at_editor_size_changed (self, *args):
        if self.cal_button.get_active ():
            x, y = self.window.get_position ()
            height, width = self.window.get_size ()
            if ((x != self.x) or (y != self.y) or (height != self.height) or (width != self.width)):
                self.__hide_calendar__ ()

    def on_cb_xoutput_toggled (self, *args):
        if self.cb_xoutput.get_active ():
            self.output = 1
        else:
            self.output = 0

    def on_cal_button_toggled (self, *args):
        if self.cal_button.get_active ():
            self.__show_calendar__ ()
        else:
            self.__hide_calendar__ ()


    def __setup_calendar__ (self):
        if self.cal_loaded == False:


            self.cal_window = self.builder.get_object("cal_window")
            self.calendar = self.builder.get_object("calendar")
            
            self.calendar.connect("focus-out-event", self.on_cal_lost_focus)
            self.cal_window.connect("destroy", self.__destroy_calendar__) # its actually not destroyed, but deleted
            self.cal_window.connect("focus-out-event", self.__destroy_calendar__) # its actually not destroyed, but deleted

            self.calendar.connect("day-selected-double-click", self.on_cal_day_selected_dc)
            self.calendar.connect("day-selected", self.on_cal_day_selected)
            
            
            self.cal_window.hide()
            self.cal_loaded = True

    def __destroy_calendar__ (self):
        self.cal_window.hide()
        return True

    def on_cal_day_selected (self, *args):
        if self.cal_active:
            year, month, day = self.calendar.get_date ()
            self.spin_year.set_value (int (year))
            self.spin_month.set_value (int (month) + 1)
            self.spin_day.set_value (int (day))

    def on_cal_day_selected_dc (self, *args):
        self.__hide_calendar__ ()

    def __show_calendar__ (self):
        x, y = self.window.get_position()
        button_rect = self.cal_button.get_allocation()
        x = x + button_rect.x
        y = y + button_rect.y + (button_rect.height * 2)
        self.cal_window.move (x, y)
        self.window.set_modal (False)
        self.x, self.y = self.window.get_position ()
        self.height, self.width = self.window.get_size ()
        self.cal_active = False
        self.calendar.select_month (self.spin_month.get_value_as_int () -1 , self.spin_year.get_value_as_int ())
        self.calendar.select_day (self.spin_day.get_value_as_int ())
        self.cal_active = True
        self.cal_window.show_all ()

    def __hide_calendar__ (self):
        self.cal_window.hide()
        self.cal_button.set_active (False)
        self.window.set_modal (True)


    def on_worded_label_event (self, *args):
        #TODO highlight on mouseover
        pass

    def on_defined_label_event (self, *args):
        #TODO highlight on mouseover
        # enable control_option on click
        pass

    def on_text_task_popup_menu (self, *args):
        #TODO show at_script_menuons: install t
        # don't forget to attach eventhandling to this popup
        pass



    def on_text_task_change (self, *args):
        start = self.text_task_buffer.get_start_iter()
        end = self.text_task_buffer.get_end_iter()
        self.command = self.text_task_buffer.get_text(start, end, False)


    def on_entry_title_changed (self, *args):
        self.title = self.entry_title.get_text()

    def on_spin_day_changed (self, *args):
        self.__check_spins__ ()
        self.__update_time_cal__()

    def on_spin_month_changed (self, *args):
        self.__check_spins__ ()
        self.__update_time_cal__()

    def on_spin_year_changed (self, *args):
        self.__check_spins__ ()
        self.__update_time_cal__()

    def on_spin_hour_changed (self, *args):
        self.__check_spins__ ()
        self.__update_time_cal__()

    def on_spin_minute_changed (self, *args):
        self.__check_spins__ ()
        self.__update_time_cal__()

    def __check_spins__ (self):
        # Is additionally run every minute
        if self.check_spin_running != True:
            self.check_spin_running = True

            ctime = time.localtime()
            year = ctime[0]
            month = ctime[1]
            day = ctime[2]
            hour = ctime[3]
            minute = ctime[4]

            cyear = False
            cmonth = False
            cday = False
            chour = False

            syear = self.spin_year.get_value_as_int ()
            if (syear == year):
                cyear = True

            smonth = self.spin_month.get_value_as_int ()
            mi, ma = self.spin_month.get_range ()
            if cyear:
                if (mi != month):
                    self.spin_month.set_range (month, 12)
                    mi = month
            else:
                if ((mi != 1) or (ma != 12)):
                    self.spin_month.set_range (1, 12)
            if (mi <= smonth <= ma):
                self.spin_month.set_value (smonth)
            else:
                if (smonth > ma):
                    self.spin_month.set_value (ma)
                else:
                    self.spin_month.set_value (mi)
            smonth = self.spin_month.get_value_as_int ()
            if (smonth == month):
                cmonth = True

            sday = self.spin_day.get_value_as_int ()
            mi, ma = self.spin_day.get_range ()
            w, days = calendar.monthrange (syear, smonth)
            if (cmonth and cyear):
                if (mi != day):
                    self.spin_day.set_range (day, days)
                    mi = day
            else:
                if ((mi != 1) or (ma != days)):
                    self.spin_day.set_range (1, days)
            if (mi <= sday <= days):
                self.spin_day.set_value (sday)
            else:
                if (sday > days):
                    self.spin_day.set_value (days)
                else:
                    self.spin_day.set_value (mi)
            sday = self.spin_day.get_value_as_int ()
            if (sday == day):
                cday = True

            shour = self.spin_hour.get_value_as_int ()
            mi, ma = self.spin_hour.get_range ()
            
            if (cyear and cmonth and cday):
                if (mi != hour):
                    self.spin_hour.set_range (hour, self.HOUR_MAX)
                    mi = hour
            else:
                if ((mi != 0) or (ma != 24)):
                    self.spin_hour.set_range (0, self.HOUR_MAX)
            if (mi <= shour <= ma):
                self.spin_hour.set_value (shour)
            else:
                if (shour > ma):
                    self.spin_hour.set_value (ma)
                else:
                    self.spin_hour.set_value (mi)
            shour = self.spin_hour.get_value_as_int ()
            if (shour == hour):
                chour = True

            sminute = self.spin_minute.get_value_as_int ()
            mi, ma = self.spin_minute.get_range ()
            if (cyear and cmonth and cday and chour):
                if (mi != minute):
                    self.spin_minute.set_range (minute, 59)
                    mi = minute
            else:
                if ((mi != 0) or (ma != 59)):
                    self.spin_minute.set_range (0, 59)
            if (mi <= sminute <= ma):
                self.spin_minute.set_value (sminute)
            else:
                if (sminute > ma):
                    self.spin_minute.set_value (ma)
                else:
                    self.spin_minute.set_value (mi)
            self.check_spin_running = False


    def __update_time_cal__ (self):
        year = self.spin_year.get_text ()
        month = self.spin_month.get_text ()
        day = self.spin_day.get_text ()
        hour = self.spin_hour.get_text()
        minute = self.spin_minute.get_text()

        year = str(year)

        if hour.isdigit():
            hour = int(hour)
        else:
            return False

        if minute.isdigit():
            minute = int(minute)
        else:
            return False

        if day.isdigit ():
            day = int (day)
        else:
            return False

        if month.isdigit ():
            month = int (month)
        else:
            return False

        if year.isdigit () == False:
            return False

        if hour < 10:
            hour = "0" + str(hour)
        else:
            hour = str(hour)

        if minute < 10:
            minute = "0" + str(minute)
        else:
            minute = str(minute)

        if month < 10:
            month = "0" + str(month)
        else:
            month = str(month)

        if day < 10:
            day = "0" + str(day)
        else:
            day = str(day)

        self.runat = hour + minute + " " + day + "." + month + "." + year


    def popup_error_no_digit (self, field):
        box_popup = Gtk.MessageDialog (self.window, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, _("In one or both of the fields hour and minute there was entered a letter, or a number out of range. Remember an hour only has 60 minutes and a day only 24 hours."))
        box_popup.set_response_sensitive(Gtk.ResponseType.OK, True)
        run = box_popup.run ()
        box_popup.hide ()
        field.set_text ("0")


    def __reset__ (self):
        self.title = _("Untitled")
        self.command = ""

        ctime = time.localtime()
        year = ctime[0]
        month = ctime[1]
        day = ctime[2]
        hour = ctime[3]
        minute = ctime[4]

        self.output = 0

        self.runat = str(hour) + str(minute) + " " + str(day) + "." + str(month) + "." + str (year)

        self.spin_hour.set_value(int(hour))
        self.spin_minute.set_value(int(minute))
        self.spin_year.set_value (int (year))
        self.spin_month.set_value (int (month))
        self.spin_day.set_value (int (day))

        self.__update_textboxes__ ()


    def __update_textboxes__(self, update_runat = 1):

        if self.title == None:
            self.title = _("Untitled")

        self.entry_title.set_text(self.title)
        self.text_task_buffer.set_text(self.command)

    def __parse_time__ (self, time, date):
        regexp_date = re.compile("([0-9][0-9])\.([0-9][0-9])\.([0-9][0-9][0-9][0-9])")
        regexp_time = re.compile("([0-9][0-9]):([0-9][0-9])")

        time_g = regexp_time.match(time)
        if time_g:
            (hour, minute) = time_g.groups()

        date_g = regexp_date.match(date)
        if date_g:
            (day, month, year) = date_g.groups()

        return hour, minute, day, month, year


    def on_button_cancel_clicked (self, *args):
		
        self.__destroy_calendar__ ()
        
        if self.mode == 2:
           self.ParentClass.template_manager.reload_tv()
           self.ParentClass.template_manager.window.show()		
           self.window.hide()	
        else:
           self.window.hide()
            
        return True


    def __WrongRecordDialog__ (self, x):
        self.wrongdialog = Gtk.MessageDialog(self.window, Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, (_("This is an invalid record! The problem could be: %s") % (x)))
        self.wrongdialog.run()
        self.wrongdialog.destroy()

    def on_button_template_clicked (self, *args):
        self.template.savetemplate_at (0, self.title, self.command, self.output)
        self.window.hide ()

    def on_button_save_clicked (self, *args):
		
        self.__hide_calendar__ ()
		
        if self.mode == 2:
            self.template.savetemplate_at(self.tid, self.title, self.command, self.output)
            self.ParentClass.template_manager.reload_tv()
            self.ParentClass.template_manager.window.show()
            self.window.hide()
            return

        (validate, reason) = self.scheduler.checkfield(self.runat)
  
        if validate == False:
            self.__WrongRecordDialog__(reason)
            return

        if (self.backend.get_not_inform_working_dir_at() != True):
            dia2 = Gtk.MessageDialog (self.window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.WARNING, Gtk.ButtonsType.NONE, _("Note about working directory of executed tasks:\n\nOne-time tasks will be run from the directory where Gnome schedule is run from (normally the home directory)."))
            dia2.add_buttons (_("_Don't show again"), Gtk.ResponseType.CLOSE, Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
            dia2.set_title (_("Warning: Working directory of executed tasks"))
            response = dia2.run ()
            if response == Gtk.ResponseType.CANCEL:
                dia2.destroy ()
                del dia2
                return
            elif response == Gtk.ResponseType.CLOSE:
                self.backend.set_not_inform_working_dir_at (True)
            else:
                pass
            dia2.destroy ()
            del dia2

        if self.mode == 1:
            self.scheduler.update(self.job_id, self.runat, self.command, self.title, self.output)
        else:
            self.scheduler.append(self.runat, self.command, self.title, self.output)

        self.ParentClass.schedule_reload()
		
        self.window.hide ()


