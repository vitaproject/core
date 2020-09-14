#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import numpy as np
from matplotlib import pyplot as plt
import math

from vita.modules.projection.projection2D.field_line.field_line import FieldLine
from vita.modules.equilibrium.fiesta import Fiesta
from vita.modules.utils import intersection
from vita.utility import get_resource
from vita.modules.utils.getOption import getOption

R200 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
FIESTA = Fiesta(R200)
field_line = FieldLine(FIESTA)

R = field_line.fiesta_equil.get_midplane_lcfs()[0]
r0 = R - 0.01
rf = R - 0.02
midplane_range = np.linspace(r0,rf,3)
points = []
lengths = []
for r in midplane_range:
    points.append( [r,0,0] )
    lengths.append( 20 )
print(lengths)
field_line_dict = []
for idx, val in enumerate(points):
    field_line_dict.append( field_line.follow_field_in_plane(val, lengths[idx], break_at_limiter=False) )

field_lines = []
for fl in field_line_dict:
    field_lines.append( np.array([ fl['R'], fl['Z'] ]) )

divertor_points = 3
#divertor_x = np.linspace( 1.9, 2.45,divertor_points)
#divertor_y = np.linspace(-3,-3.6,divertor_points)
divertor_x = np.array([0.1485, 0.1525, 0.159])
divertor_y = np.array([0.9, 0.75, 0.6])
divertor_xy = np.array([divertor_x, divertor_y])

result = np.array([intersection(i, divertor_xy) for i in field_lines])
(x_p, y_p) = zip (*result[:,1])

for i in field_line_dict:
    plt.plot(i['R'],i['Z'],c='r')
plt.plot(divertor_x,divertor_y,c='g')
plt.plot(x_p,y_p,'*k')
plt.gca().set_aspect('equal', adjustable='box')
plt.gca().set_ylim([0.2,1])
plt.gca().set_xlim([0, 0.8])

imageFile = getOption('imageFile')
if imageFile :
  plt.savefig(imageFile)
else :
  plt.show()

print(midplane_range)
fx = []
for i in range(len(midplane_range)-1):
    fx.append( math.hypot(x_p[i] - x_p[i+1], y_p[i] - y_p[i+1]) /
              ( midplane_range[i] - midplane_range[i+1] ) *
              ( x_p[i] / midplane_range[i] )
             )
print("Flux_expansion = ", fx)
