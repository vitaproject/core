#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import numpy as np
from matplotlib import pyplot as plt

from vita.modules.projection.projection2D.field_line.field_line import FieldLine
from vita.utility import get_resource

R200 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
field_line =  FieldLine(R200)
R = field_line.fiesta_equil.get_midplane_lcfs()[0]
print(R)
r0 = 0.45
rf = R-0.1
midplane_range = np.linspace(rf,r0,5)
points = []
lengths = []
for r in midplane_range:
    points.append( [r,0,0] )
    lengths.append( 120 )
print(lengths)
field_line_dict = []
for idx, val in enumerate(points):
    field_line_dict.append(field_line.follow_field_in_plane(val, lengths[idx], break_at_limiter=True))
#    p1 = [3.15,0,0]
#    field_line_dict.append( field_line.followFieldinPlane(p0=p1, maxl=40.0) )
f, ax = plt.subplots(1)
for i in field_line_dict:
    ax.plot(i['R'],i['Z'])
    ax.plot(i['R'],i['Z'])
f.gca().set_aspect('equal', adjustable='box')
f.gca().set_ylim([0,1])
plt.show()
print (len(field_line_dict))
