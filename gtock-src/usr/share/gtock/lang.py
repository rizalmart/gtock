# -*- coding: UTF-8 -*-
# lang.py: Translation helper functions, mainly for human readable time expressions
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

# Don't touch the first line :-) unless you know why and you need to touch
# it for your language. Also if you changed the formatting using your
# editor (and tested everything, haha)

# python modules
import inspect
import sys
import time
import warnings
warnings.filterwarnings("once", "Locale not supported by Python. Using the fallback 'C' locale.")

# Dear translators,

# This file is yours. YOU people do whatever you wan't with it. You can
# fix spelling problems, add comments, add code and functionality. You
# don't have to inform me about changes (you can commit if you have such
# an account on GNOME) yet you CAN ask the programmers for assistance.

# Yes yours. Really

# No seriously, it's yours. Yeah, yours. It's your file. You do whatever
# you want with this file. I mean it. Yes...

# If you don't have access you can create a diff file and send it to the
# AUTHORS: cd src/; cvs diff -u lang.py > language.diff  and we will
# weed it out for you. We will provide you with the best assistance
# possible.

# WHY, WHY THE HELL WHY??? WHHHAAAYYYY??????!!!!!!
# ------------------------------------------------

# Most languages will not have to do all this, but some do.
# http://lists.gnome.org/archives/gnome-i18n/2004-June/msg00089.html

# To get numeric nth translations correct, some languages need to get
# things like the gender and wording correct. The only way to do
# this is to code it.

# Therefor I am making it possible for those languages to code it, in
# this file.

# Read through the comments of the implementations of other languages
# and don't touch the implementation for English unless you know what
# you are doing.

# If your language 'can' get correctly translated by using only the po
# files, it means that you don't have to touch these files at all. In
# that case the advice is simple: don't touch it. hehe :)


import config


##
## I18N
##
import locale
import gettext
domain = config.GETTEXT_PACKAGE()
gettext.bindtextdomain(domain, config.GNOMELOCALEDIR())
gettext.textdomain(domain)
_ = gettext.gettext

# Fallback to english if locale setting is unknown
# or translation for this locale is not available
if gettext.find(domain) == None:
    language = "C"
else:
    language = ""
try:
    locale.setlocale(locale.LC_ALL, language)
except:
    warnings.warn_explicit("Locale not supported by Python. Using the fallback 'C' locale.", Warning, "lang.py", sys.exc_info()[2].tb_frame.f_back.f_lineno)

encoding = locale.getpreferredencoding(False)
language = locale.getlocale()[0]
if language == None:
    language = "C"

# Some locale stuff in this section to get
# translated time expressions out of system.
# Don't touch this. Change settings through gettext (po files)
def lc_weekday (weekday):
    weekday = int(weekday)
    if weekday >= 0 and weekday < 7:
        weekday = str(weekday)
    else:
        weekday = "0"
    timevalue = time.strptime(weekday, "%w")
    expression = time.strftime("%A", timevalue)
    return str(expression)

def lc_month (month):
    month = "%02d" % int(month)
    timevalue = time.strptime(month, "%m")
    expression = time.strftime("%B", timevalue)
    return str(expression)

def lc_date (day,month,year = None):
    day = "%02d" % int(day)
    month = "%02d" % int(month)
    if year == None:
        timevalue = time.strptime(("%s.%s" % (day, month)), "%d.%m")
        # Translators: Date format for expressions like 'January 21'. %B is month, %d is day number.
        # Run the command 'man strftime' to read more about these and other available specifiers.
        expression = time.strftime(_("%B %d"), timevalue)
    else:
        year = str(year)[-2:]
        year = "%02d" % int(year)
        timevalue = time.strptime(("%s.%s.%s" % (day, month, year)), "%d.%m.%y")
        # Translators: Date format for expressions like 'January 21, 2005'. %B is month, %d is day number, %Y is year with century.
        # Run the command 'man strftime' to read more about these and other available specifiers.
        expression = time.strftime(_("%B %d, %Y"), timevalue)
    return str(expression)

def lc_time (hour,minute,second = None):
    hour = "%02d" % int(hour)
    minute = "%02d" % int(minute)
    if second == None:
        timevalue = time.strptime(("%s:%s" % (hour, minute)), "%H:%M")
        # Translators: Time without seconds. %H is hour, %M is minute.
        # Run the command 'man strftime' to read more about these and other available specifiers.
        expression = time.strftime(_("%H:%M"), timevalue)
    else:
        second = "%02d" % int(second)
        timevalue = time.strptime(("%s:%s:%s" % (hour, minute, second)), "%H:%M:%S")
        expression = time.strftime("%X", timevalue)
    return str(expression)


# So this is for the really really hard languages that have changing
# genders and word-ordering depending on the nth-numeric value.
# You can copy-and-paste the whole block and start adjusting it for your
# language. If you need assistance, read the AUTHORS file and try to
# contact us or use the mailinglists.
def translate_crontab_easy (minute, hour, day, month, weekday):
#   Add support for your language here
#   if language.find ("whatever") != -1:
#       return translate_crontab_easy_whatever (minute, hour, day, month, weekday)
#   else:
        return translate_crontab_easy_common (minute, hour, day, month, weekday)

# Translate Crontab expressions to human readable ones.
# Don't touch this function. Copy and modify it to create a special translation.
# Changes on this function affects all translations made through po files.
def translate_crontab_easy_common (minute, hour, day, month, weekday):

    # reboot
    if minute == "@reboot":
        return _("At reboot")

    # These are unsupported cases
    if minute.find ("/") != -1 or hour.find ("/") != -1 or day.find ("/") != -1 or month.find ("/") != -1 or weekday.find ("/") != -1:
        return translate_crontab_easy_fallback (minute, hour, day, month, weekday)
    if minute.find ("-") != -1 or hour.find ("-") != -1 or day.find ("-") != -1 or month.find ("-") != -1 or weekday.find ("-") != -1:
        return translate_crontab_easy_fallback (minute, hour, day, month, weekday)
    if minute.find (",") != -1 or hour.find (",") != -1 or day.find (",") != -1 or month.find (",") != -1 or weekday.find (",") != -1:
        return translate_crontab_easy_fallback (minute, hour, day, month, weekday)

    # So if our case is supported:

    # Minute and hour cases
    if month == "*" and day == "*" and weekday == "*":
        if minute == "0" and hour == "*":
            return _("At every full hour")
        elif minute == "*" and hour == "*":
            return _("At every minute")
        elif minute != "*" and hour == "*":
            return (_("At minute %(minute)s of every hour") % { "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("At every minute between %(time_from)s and %(time_to)s") % { "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif hour != "*" and minute != "*":
            return (_("On every day at %(time)s") % { "time": lc_time(hour, minute) } )

    # Day cases
    if month == "*" and day != "*" and weekday == "*":
        if minute == "0" and hour == "*":
            return (_("On day %(monthday)s of every month at every full hour") % { "monthday": str(day) } )
        elif minute == "*" and hour == "*":
            return (_("On day %(monthday)s of every month at every minute") % { "monthday": str(day) } )
        elif minute != "*" and hour == "*":
            return (_("On day %(monthday)s of every month at minute %(minute)s of every hour") % { "monthday": str(day), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("On day %(monthday)s of every month at every minute between %(time_from)s and %(time_to)s") % { "monthday": str(day), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("On day %(monthday)s of every month at %(time)s") % { "monthday": str(day), "time": lc_time(hour, minute) } )

    # Month cases
    if month != "*" and weekday == "*" and day == "*":
        if minute == "0" and hour == "*":
            return (_("On every day in %(month)s at every full hour") % { "month": lc_month(month) } )
        elif minute == "*" and hour == "*":
            return (_("On every day in %(month)s at every minute") % { "month": lc_month(month) } )
        elif minute != "*" and hour == "*":
            return (_("On every day in %(month)s at minute %(minute)s of every hour") % { "month": lc_month(month), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("On every day in %(month)s at every minute between %(time_from)s and %(time_to)s") % { "month": lc_month(month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("On every day in %(month)s at %(time)s") % { "month": lc_month(month), "time": lc_time(hour, minute) } )

    # Day and month cases
    if month != "*" and weekday == "*" and day != "*":
        if minute == "0" and hour == "*":
            return (_("Every year on %(date)s at every full hour") % { "date": lc_date(day,month) } )
        elif minute == "*" and hour == "*":
            return (_("Every year on %(date)s at every minute") % { "date": lc_date(day,month) } )
        elif minute != "*" and hour == "*":
            return (_("Every year on %(date)s at minute %(minute)s of every hour") % { "date": lc_date(day,month), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("Every year on %(date)s at every minute between %(time_from)s and %(time_to)s") % { "date": lc_date(day,month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("Every year on %(date)s at %(time)s") % { "date": lc_date(day,month), "time": lc_time(hour, minute) } )

    # Weekday cases
    if month == "*" and day == "*" and weekday != "*":
        if minute == "0" and hour == "*":
            return (_("On every weekday: %(weekday)s at every full hour") % { "weekday": lc_weekday(weekday) } )
        elif minute == "*" and hour == "*":
            return (_("On every weekday: %(weekday)s at every minute") % { "weekday": lc_weekday(weekday) } )
        elif minute != "*" and hour == "*":
            return (_("On every weekday: %(weekday)s at minute %(minute)s of every hour") % { "weekday": lc_weekday(weekday), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("On every weekday: %(weekday)s at every minute between %(time_from)s and %(time_to)s") % { "weekday": lc_weekday(weekday), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("On every weekday: %(weekday)s at %(time)s") % { "weekday": lc_weekday(weekday), "time": lc_time(hour, minute) } )

    # Day and weekday cases
    if day != "*" and month == "*" and weekday != "*":
        if minute == "0" and hour == "*":
            return (_("On day %(monthday)s of every month and every weekday: %(weekday)s at every full hour") % { "monthday": str(day), "weekday": lc_weekday(weekday) } )
        elif minute == "*" and hour == "*":
            return (_("On day %(monthday)s of every month and every weekday: %(weekday)s at every minute") % { "monthday": str(day), "weekday": lc_weekday(weekday) } )
        elif minute != "*" and hour == "*":
            return (_("On day %(monthday)s of every month and every weekday: %(weekday)s at minute %(minute)s of every hour") % { "monthday": str(day), "weekday": lc_weekday(weekday), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("On day %(monthday)s of every month and every weekday: %(weekday)s at every minute between %(time_from)s and %(time_to)s") % { "monthday": str(day), "weekday": lc_weekday(weekday), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("On day %(monthday)s of every month and every weekday: %(weekday)s at %(time)s") % { "monthday": str(day), "weekday": lc_weekday(weekday), "time": lc_time(hour, minute) } )

    # Month and weekday cases
    if day == "*" and month != "*" and weekday != "*":
        if minute == "0" and hour == "*":
            return (_("On every weekday: %(weekday)s in %(month)s at every full hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month) } )
        elif minute == "*" and hour == "*":
            return (_("On every weekday: %(weekday)s in %(month)s at every minute") % { "weekday": lc_weekday(weekday), "month": lc_month(month) } )
        elif minute != "*" and hour == "*":
            return (_("On every weekday: %(weekday)s in %(month)s at minute %(minute)s of every hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("On every weekday: %(weekday)s in %(month)s at every minute between %(time_from)s and %(time_to)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("On every weekday: %(weekday)s in %(month)s at %(time)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "time": lc_time(hour, minute) } )

    # Day, month and weekday cases
    if day != "*" and month != "*" and weekday != "*":
        if minute == "0" and hour == "*":
            return (_("On every weekday: %(weekday)s in %(month)s and on %(date)s every year at every full hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month) } )
        elif minute == "*" and hour == "*":
            return (_("On every weekday: %(weekday)s in %(month)s and on %(date)s every year at every minute") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month) } )
        elif minute != "*" and hour == "*":
            return (_("On every weekday: %(weekday)s in %(month)s and on %(date)s every year at minute %(minute)s of every hour") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month), "minute": str(minute) } )
        elif minute == "*" and hour != "*":
            return (_("On every weekday: %(weekday)s in %(month)s and on %(date)s every year at every minute between %(time_from)s and %(time_to)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month), "time_from": lc_time(hour, 0), "time_to": lc_time(hour, 59) } )
        elif minute != "*" and hour != "*":
            return (_("On every weekday: %(weekday)s in %(month)s and on %(date)s every year at %(time)s") % { "weekday": lc_weekday(weekday), "month": lc_month(month), "date": lc_date(day,month), "time": lc_time(hour, minute) } )

    # If nothing got translated, we fall back to ...
    return translate_crontab_easy_fallback (minute, hour, day, month, weekday)

# This is for cases that don't be covered by translate_crontab_easy
def translate_crontab_easy_fallback (minute, hour, day, month, weekday):
    if minute == "*":
        minute = _("every minute")
    else:
        minute = _("minute: %s") % (minute)

    if hour == "*":
        hour = _("every hour")
    else:
        hour = _("hour: %s") % (hour)

    if day == "*":
        day = _("every day of month")
    else:
        day = _("day of month: %s") % (day)

    if month == "*":
        month = _("every month")
    else:
        month = _("month: %s") % (month)

    if weekday == "*":
        return _("At %(minute)s, %(hour)s, %(monthday)s, %(month)s") % { "minute": minute, "hour": hour, "monthday": day, "month": month }
    else:
        weekday = _("weekday: %s") % (weekday)
        return _("At %(minute)s, %(hour)s, %(monthday)s, %(month)s, %(weekday)s") % { "minute": minute, "hour": hour, "monthday": day, "month": month, "weekday": weekday }
