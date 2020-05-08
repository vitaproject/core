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

########################
# load the equilibrium #
R200 = get_resource("ST40-IVC1", "equilibrium", "eq_006_2T_export")
FIESTA = Fiesta(R200)
field_line =  FieldLine(FIESTA)

# TBC

