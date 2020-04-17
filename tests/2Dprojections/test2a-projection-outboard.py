#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import numpy as np
from matplotlib import pyplot as plt

from vita.modules.equilibrium.fiesta import Fiesta
from vita.modules.projection.projection2D.field_line.field_line import FieldLine
from vita.utility import get_resource
from vita.modules.utils.getOption import getOption

R200 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
FIESTA = Fiesta(R200)
field_line =  FieldLine(FIESTA)

R = FIESTA.get_midplane_lcfs()[1]
r0 = 0.45
rf = R+0.01
midplane_range = np.linspace(r0,rf,3)
points = []
lengths = []
for r in midplane_range:
    points.append( [r,0,0] )
    lengths.append( 60 - (r-r0)*120 )
print(lengths)
field_line_dict = []
for idx, val in enumerate(points):
    field_line_dict.append(field_line.follow_field_in_plane(val, lengths[idx], break_at_limiter=False) )
f, ax = plt.subplots(1)
for i in field_line_dict:
    ax.plot(i['R'],i['Z'])
    ax.plot(i['R'],i['Z'])
f.gca().set_aspect('equal', adjustable='box')
f.gca().set_ylim([-1.0, 0])


imageFile = getOption('imageFile')
if imageFile :
  plt.savefig(imageFile)
else :
  plt.show()
