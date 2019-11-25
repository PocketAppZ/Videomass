# -*- coding: UTF-8 -*-

#########################################################
# Name: os_interaction.py
# Porpose: module with standard tools for OS
# Compatibility: Python3, wxPython Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev December 28 2018
#########################################################

# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################

"""
The module contains some useful function for copying, moving, deleting 
and renaming files and folders.

"""
import shutil
import os
import glob
import math

#------------------------------------------------------------------------
def format_bytes(n):
    """
    Given a float number (bytes) returns size output 
    strings human readable, e.g.
    out = format_bytes(9909043.20)
    It return a string digit with metric suffix
    
    """
    unit = ["B", "KiB", "MiB", "GiB", "TiB", 
            "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0
    
    if n == 0.0: # if 0.0 or 0 raise ValueError: math domain error
        exponent = 0
    else:
        exponent = int(math.log(n, const)) # get unit index

    suffix = unit[exponent] # unit index
    output_value = n / (const ** exponent)

    return "%.2f%s" % (output_value, suffix)
#------------------------------------------------------------------------

def to_bytes(string):
    """
    Convert given size string to bytes, e.g. 
    out = to_bytes('9.45MiB')
    It return a number 'float' 
    
    """
    value = 0.0
    unit = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    const = 1024.0

    for index, metric in enumerate(reversed(unit)):
        if metric in string:
            value = float(string.split(metric)[0])
            break

    exponent = index * (-1) + (len(unit) - 1)

    return round(value * (const ** exponent), 2)
#------------------------------------------------------------------------

def time_seconds(time):
    """
    convert time human to seconds
    
    """
    if time == 'N/A':
        return int('0')
    
    pos = time.split(':')
    h,m,s = pos[0],pos[1],pos[2]
    duration = (int(h)*60+ int(m)*60+ float(s))
    
    return duration

#------------------------------------------------------------------------
def time_human(seconds):
    """
    Convert from seconds to time human. Accept integear only e.g.
    time_human(2300)
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)