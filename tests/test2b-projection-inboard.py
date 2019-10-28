#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import numpy as np
from matplotlib import pyplot as plt
import sys
import pathlib

path_modules = pathlib.Path('../vita/modules')
if str(path_modules) not in sys.path:
    sys.path.append(str(path_modules)) # Adds higher directory to python modules path.
path_utils = pathlib.Path('../vita/modules/utils')
if str(path_utils) not in sys.path:
    sys.path.append(str(path_utils)) # Adds higher directory to python modules path.
print(sys.path)

from fiesta.fiesta_interface import Fiesta

filepath = "T:\\USERS\\J_Wood\\STF1_equilibriums\\export_R200.mat"
field_line = Fiesta(filepath)
R = field_line.getMidplaneLCFS()
r0 = 0.6
rf = 1.
midplane_range = np.linspace(r0,rf,10)
points = []
lengths = []
for r in midplane_range:
    points.append( [r,0,0] )
    lengths.append( 120 )
print(lengths)
field_line_dict = []
for idx, val in enumerate(points):
    field_line_dict.append( field_line.followFieldinPlane(val, lengths[idx]) )
#    p1 = [3.15,0,0]
#    field_line_dict.append( field_line.followFieldinPlane(p0=p1, maxl=40.0) )
f, ax = plt.subplots(1)
for i in field_line_dict:
    ax.plot(i['R'],i['Z'])
    ax.plot(i['R'],i['Z'])
f.gca().set_aspect('equal', adjustable='box')
f.gca().set_ylim([0,4])
print (len(field_line_dict))