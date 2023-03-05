# config.py - build time configuration
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

version = "3.0.0"

gtk_version="3.0"

image_dir = "/usr/share/gtock/pixmaps"
gs_dir = "/usr/share/gtock"
glade_dir = gs_dir + "/assets"
xwrapper_exec = "python3 /usr/share/gtock/xwrapper.py"
locale_dir = "/usr/share/locale"
crontabbin = "/usr/bin/crontab"
atbin = "/usr/bin/at"
atqbin = "/usr/bin/atq"
atrmbin = "/usr/bin/atrm"
batchbin = "/usr/bin/batch"
subin = "/bin/su"
prefix = "/usr"

import os

def getGtkVersion():
	return gtk_version

def getConfigDir():
	return os.environ['HOME'] + "/.config/gtock"

def getPrefix():
	return prefix

def getSubin ():
	return subin

def getAtbin ():
	return atbin

def getAtrmbin ():
	return atrmbin

def getAtqbin ():
	return atqbin

def getBatchbin ():
	return batchbin

def getCrontabbin ():
	return crontabbin

def getVersion ():
	return version

def getImagedir ():
	return image_dir

def getGladedir ():
	return glade_dir

def GETTEXT_PACKAGE():
	return "gtock"

def GNOMELOCALEDIR():
	return locale_dir
	
def atInstalled():
	return os.path.exists(atbin)
	
def cronTabInstalled():
	return os.path.exists(crontabbin)
