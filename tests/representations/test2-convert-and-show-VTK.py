#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 18:28:22 2019

@author: Daniel.Ibanez
"""
import numpy as np
from matplotlib import pyplot as plt
from os.path import join as pjoin
import os
from vita.modules.equilibrium.fiesta import Fiesta
from vita.modules.representation.psi_map import PsiRepresentation
from vita.utility import get_resource, add_resource
from vita.modules.utils.getOption import getOption

########################
# load the equilibrium #
EQ_NAME = "eq_006_2T_export"
FIESTA_FILE = get_resource("ST40-IVC1", "equilibrium", EQ_NAME)
print("Processing file: " + FIESTA_FILE)

PSI_REPRESENTATION = PsiRepresentation(FIESTA_FILE)
PSI_REPRESENTATION.psiVTK()
PSI_REPRESENTATION.visualize2D()
PSI_REPRESENTATION.visualize3D()
