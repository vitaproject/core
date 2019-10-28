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

from modelFiesta.fiestaInterface import FieldLines

filepath = "T:\\USERS\\J_Wood\\STF1_equilibriums\\export_R200.mat"
field_line = FieldLines(filepath)
R = field_line.getMidplaneLCFS()
r0 = 3.05
rf = 3.1
midplane_range = np.linspace(r0,rf,3)
points = []
lengths = []
for r in midplane_range:
    points.append( [r,0,0] )
    lengths.append( 60 - (r-r0)*120 )
print(lengths)
field_line_dict = []
for idx, val in enumerate(points):
    field_line_dict.append( field_line.followFieldinPlane(val, lengths[idx]) )
f, ax = plt.subplots(1)
for i in field_line_dict:
    ax.plot(i['R'],i['Z'])
    ax.plot(i['R'],i['Z'])
f.gca().set_aspect('equal', adjustable='box')
f.gca().set_ylim([-4,0])
print (len(field_line_dict))