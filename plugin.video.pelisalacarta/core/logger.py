# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta 4
# Copyright 2015 tvalacarta@gmail.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of pelisalacarta 4.
#
# pelisalacarta 4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pelisalacarta 4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pelisalacarta 4.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------------------
# Logger (kodi)
#------------------------------------------------------------

from core import config
loggeractive = (config.get_setting("debug")=="true")

import xbmc

def log_enable(active):
    global loggeractive
    loggeractive = active

def info(texto):
    if loggeractive:
        try:
            xbmc.log(texto)
        except:
            # FIXME: ¿Esto de que falle al poner un log no se puede resolver con un encode("ascii",errors="ignore") ?
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)

def debug(texto):
    if loggeractive:
        try:
            import inspect
            import os
            last=inspect.stack()[1]
            modulo= os.path.basename(os.path.splitext(last[1])[0])
            funcion= last [3]
            texto= "    [" + modulo + "." + funcion + "] " + texto
            xbmc.log("######## DEBUG #########")
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)

def error(texto):
    if loggeractive:
        try:
            import inspect
            import os
            last=inspect.stack()[1]
            modulo= os.path.basename(os.path.splitext(last[1])[0])
            funcion= last [3]
            texto= "    [" + modulo + "." + funcion + "] " + texto
            xbmc.log("######## ERROR #########")
            xbmc.log(texto)
        except:
            validchars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in texto if c in validchars)
            xbmc.log("(stripped) "+stripped)
