# db.py - db class to store database of crontab and at tasks
# Copyright (C) 2011 Gaute Hope <eg at gaute dot vetsj dot com>
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

# Using Pythons pickle to dump tasks
class GnomeScheduleDB:
  VERSION = 1

  # Format:
  # [title, time, preview, line, output]
  crontab = []


  # Format:
  # [title, date, time, preview, script, output]
  at = []

  def __init__ (self):
    pass

  def setcrontab (self, c):
    self.crontab = c

  def setat (self, a):
    self.at = a


