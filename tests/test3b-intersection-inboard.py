#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import numpy as np
from matplotlib import pyplot as plt
import math

from vita.modules.fiesta import FieldLine
from vita.modules.utils import intersection

#filepath = "T:\\USERS\\J_Wood\\STF1_equilibriums\\export_R200.mat"
#filepath = "/home/daniel.iglesias/Simulations/plasma_scenarios/ST-F1/ST200/python_responses/export_R200.mat"
filepath = '/home/jmbols/Postdoc/export_R200.mat'
field_line = FieldLine(filepath)
R = field_line.fiesta_equil.get_midplane_lcfs()
r0 = 0.85
rf = 0.95
midplane_range = np.linspace(r0,rf,3)
points = []
lengths = []
for r in midplane_range:
    points.append( [r,0,0] )
    lengths.append( 120 )
print(lengths)
field_line_dict = []
for idx, val in enumerate(points):
    field_line_dict.append( field_line.follow_field_in_plane(val, lengths[idx]) )
#    p1 = [3.15,0,0]
#    field_line_dict.append( field_line.followFieldinPlane(p0=p1, maxl=40.0) )
#f, ax = plt.subplots(1)
#for i in field_line_dict:
#    ax.plot(i['R'],i['Z'])
#    ax.plot(i['R'],i['Z'])
#f.gca().set_aspect('equal', adjustable='box')
#f.gca().set_ylim([0,4])
#print (len(field_line_dict))

field_lines = []
for fl in field_line_dict:
    field_lines.append( np.array([ fl['R'], fl['Z'] ]) )

divertor_points = 3
#divertor_x = np.linspace( 1.9, 2.45,divertor_points)
#divertor_y = np.linspace(-3,-3.6,divertor_points)
divertor_x = np.array([1.01, 1.07, 1.12])
divertor_y = np.array([2.44, 2.9, 3.1])
divertor_xy = np.array([divertor_x, divertor_y])

result = np.array([intersection(i, divertor_xy) for i in field_lines])
(x_p, y_p) = zip (*result[:,1])

for i in field_line_dict:
    plt.plot(i['R'],i['Z'],c='r')
plt.plot(divertor_x,divertor_y,c='g')
plt.plot(x_p,y_p,'*k')
plt.gca().set_aspect('equal', adjustable='box')
plt.gca().set_ylim([2.2,4])
plt.show()

print(midplane_range)
fx = []
for i in range(len(midplane_range)-1):
    fx.append( math.hypot(x_p[i+1] - x_p[i], y_p[i+1] - y_p[i]) / 
              ( midplane_range[i+1] - midplane_range[i] ) *
              ( x_p[i] / midplane_range[i] )
             )
print("Flux_expansion = ", fx)
