# template.py: Handles the link to the template data stored in gconf
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


#pygobject
from gi.repository import Gio


#python modules
import os
import configparser

#gtock
import config

import gettext
import locale

from locale import gettext as _

class Template:
	def __init__ (self, parent, configbackend):
		
		self.parent = parent
#		self.configbackend = configbackend

		self.settings = self.parent.settings



	def removetemplate_at (self,template_id):
		
		installed = self.settings.get_strv("at-installed")
		newstring = installed
		
		newstring.remove(str(template_id))
		
		try:
		    os.remove(config.getConfigDir() + '/at/'+str(template_id)+'.gsat')
		except:
		   pass
			
		self.settings.set_strv("at-installed", newstring)

	def removetemplate_crontab (self,template_id):
		
		installed = self.settings.get_strv("cron-installed")
		newstring = installed
		
		newstring.remove(str(template_id))
		
		try:
		    os.remove(config.getConfigDir() + '/crontab/'+str(template_id)+'.gsct')
		except:
		   pass
			
		self.settings.set_strv("cron-installed", newstring)

	def create_new_id_crontab (self):
		
		i=self.settings.get_int("cron-last-id")
		
		if i == None:
			self.settings.set_int("cron-last-id", 1)
			return 1
		else:
			i = i + 1
			self.settings.set_int("cron-last-id", i)
			return i

	def savetemplate_crontab (self, template_id, title, command, output, timeexpression):

		if (template_id == 0):
			template_id = self.create_new_id_crontab()
		
		fconfig = configparser.ConfigParser()
		
		fconfig['crontab template'] = {
                     'title': title,
                     'exec': command,
                     'time_expression': timeexpression,
                     'output': output
                     }
					  
		with open(config.getConfigDir() + '/crontab/'+str(template_id)+'.gsct', 'w') as configfile:
				fconfig.write(configfile)
		
		installed = self.settings.get_strv("cron-installed")
		
		if installed == None:
			pass
		else:
			found = False

			for t in installed:
				if t == str (template_id):
					found = True

			if found == False:
				installed.append(str(template_id))
		
		self.settings.reset("cron-installed")		
		self.settings.set_strv("cron-installed",installed)
		
		self.parent.template_manager.reload_tv()
		self.parent.template_chooser.reload_tv()

	def gettemplateids (self, type):
		
		# Get the value of the installed templates key as a string list
		if type == "crontab":
		  strlist = self.settings.get_strv("cron-installed")
		elif type == "at":
		  strlist = self.settings.get_strv("at-installed")
		
		
		if strlist != None:
			
			ilist = strlist
			return ilist
			
		else:
			return None

	def gettemplate (self, type, template_id):
		if type == "crontab":
			try:
				
				
				fconfig = configparser.ConfigParser()
				fconfig.read(config.getConfigDir() + '/crontab/'+str(template_id)+'.gsct')


				command = fconfig.get('crontab template', 'exec')
				title = fconfig.get('crontab template', 'title')
				output = fconfig.get('crontab template', 'output')
				timeexpression = fconfig.get('crontab template', 'time_expression')

				return template_id, title, command, output, timeexpression

			except Exception as ex:
				return False

		elif type == "at":
			try:
				
				fconfig = configparser.ConfigParser()
				fconfig.read(config.getConfigDir() + '/at/' +str(template_id)+'.gsat')
				
				command = fconfig.get('at template', 'exec')
				title = fconfig.get('at template', 'title')
				output = fconfig.get('at template', 'output')
				
				return template_id, title, command, output

			except Exception as ex:
				return False

	def create_new_id_at (self):
				
		i=self.settings.get_int("at-last-id")
		
		
		if i == 0:
			self.settings.set_int("at-last-id",1)
			return 1
		else:
			i = i + 1
			self.settings.set_int("at-last-id",i)
			return i

	def savetemplate_at (self, template_id, title, command, output):
		print("savetemplate")

		
		if (template_id == 0):
			template_id = self.create_new_id_at()
		
		fconfig = configparser.ConfigParser()
		
		fconfig['at template'] = {
                     'title': title,
                     'exec': command,
                     'output': output
                     }
					  
		with open(config.getConfigDir() + '/at/'+str(template_id)+'.gsat', 'w') as configfile:
				fconfig.write(configfile) 
				
		
		installed = self.settings.get_strv("at-installed")
		
		if installed == None:
			pass
		else:
			found = False

			for t in installed:
				if t == str (template_id):
					found = True

			if found == False:
				installed.append(str(template_id))
		
		self.settings.reset("at-installed")
		self.settings.set_strv("at-installed", installed)
		
		self.parent.template_manager.reload_tv()
		self.parent.template_chooser.reload_tv()

	# TODO: output
	def format_at (self, title, command, output):
		command = self.parent.at.__make_preview__ (command, 0)
		s = "<b>" + _("Title:") + "</b> " + title + "\n<b>" + _("Command:") + "</b> " + command
		if int(output) > 0:
			s = (s + " <i>(%s)</i>") % (str (self.parent.output_strings [2]))

		return s

	def format_crontab (self, title, command, output, timeexpression):
		command = self.parent.crontab.__make_preview__ (command)
		if self.parent.edit_mode == "simple":
			# hehe.. :)
			timeexpression = timeexpression + " echo hehe"
			minute, hour, dom, moy, dow, hehe = self.parent.crontab.parse(timeexpression, True)
			timeexpression = self.parent.crontab.__easy__ (minute, hour, dom, moy, dow)

		s = "<b>" + _("Title:") + "</b> " + title + "\n<b>" + _("Run:") + "</b> " + timeexpression + "\n<b>" + _("Command:") + "</b> " + command

		if int(output) > 0:
			s = (s + " <i>(%s)</i>") % (str (self.parent.output_strings[int(output)]))

		return s
