# data.py: Contains the backend to the gconf database
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

from gi.repository import Gio

#python modules
import os

#gtock
import config

class ConfigBackend:

	def __init__(self, parent, type):
	  
		self.parent = parent
		self.type = "dconf"

		settings = Gio.Settings.new("org.gtk.gtock")

		self.settings=settings
		
		
	def get_not_inform_working_dir(self):
		if((self.get_not_inform_working_dir_crontab() and self.get_not_inform_working_dir_at()) or self.settings.get_boolean("inform-working-dir")):
			return True
		else:
			return False


	def set_not_inform_working_dir (self, value):
		self.settings.set_boolean("inform-working-dir", value)

	def get_not_inform_working_dir_crontab (self):
		return self.settings.get_boolean("inform-working-dir-crontab")

	def set_not_inform_working_dir_crontab (self, value):
		self.settings.set_boolean("inform-working-dir-crontab", value)

	def get_not_inform_working_dir_at (self):
		return self.settings.get_boolean("inform-working-dir-at")

	def set_not_inform_working_dir_at (self, value):
		self.settings.set_boolean("inform-working-dir-at", value)


	def set_window_state(self, x, y, h, w,maximized=False):
		
		#print("saving window state")
		#print("set-x: " + str(x))
		#print("set-y: " + str(y))
		#print("set-w: " + str(w))
		#print("set-h: " + str(h))
		#print("maximized: " + str(maximized))
		
		self.settings.set_int("x-axis", x)
		self.settings.set_int("y-axis", y)
		self.settings.set_int("window-height", h)
		self.settings.set_int("window-width", w)
		self.settings.set_boolean("window-maximized", maximized)

	def get_window_state(self):
		
		h = self.settings.get_int("window-height")
		w = self.settings.get_int("window-width")
		x = self.settings.get_int("x-axis")
		y = self.settings.get_int("y-axis")
		
		max1 = self.settings.get_boolean("window-maximized")
		
		#print("reading window state")
		#print("get-x: " + str(x))
		#print("get-y: " + str(y))
		#print("get-w: " + str(w))
		#print("get-h: " + str(h))
		#print("maximized: " + str(max1))
		
		return x, y, h, w, max1

	def get_advanced_option(self):
		return self.settings.get_boolean("advanced")


	def set_advanced_option(self,value):
		self.settings.set_boolean("advanced", value)


	def on_dconfkey_advanced_changed (self):
		val = self.settings.get_boolean("advanced")
		if val:
		    self.parent.switchView("advanced")
		else:
		    self.parent.switchView("simple")



