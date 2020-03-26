#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:12:22 2020

@author: jmbols
"""
import numpy as np
from vita.modules.utils.calculate_angle import calculate_angle

machine_precision = np.finfo(float).eps

v_1 = [0, 1]
v_2 = [0, -1]
assert(abs(calculate_angle(v_1, v_2) - np.pi/2.) < machine_precision)

v_1 = [0, 1]
v_2 = [0, 2]
assert(abs(calculate_angle(v_1, v_2) - np.pi/2.) < machine_precision)

v_1 = [0, 1]
v_2 = [1, 0]
assert(abs(calculate_angle(v_1, v_2)) < machine_precision)

v_1 = [0, 1]
v_2 = [-1, 0]
assert(abs(calculate_angle(v_1, v_2)) < machine_precision)

v_1 = [1, 1]
v_2 = [1, 0]
assert(abs(calculate_angle(v_1, v_2) - np.pi/4.) < machine_precision)

v_1 = [1, -1]
v_2 = [1, 0]
assert(abs(calculate_angle(v_1, v_2) - np.pi/4.) < machine_precision)
