#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:12:22 2020

@author: jmbols
"""

import sys
import unittest
import numpy as np

from vita.modules.utils.calculate_angle import calculate_angle
from vita.modules.utils.getOption import getOption


MACHINE_PRECISION = np.finfo(float).eps


class TestUtilityMethods(unittest.TestCase):

    def test_calculate_angle(self):
        """Testing the calculate_angle() utility method"""

        v_1 = [0, 1]
        v_2 = [0, -1]
        self.assertTrue(abs(calculate_angle(v_1, v_2) - np.pi/2.) < MACHINE_PRECISION)

        v_1 = [0, 1]
        v_2 = [0, 2]
        self.assertTrue(abs(calculate_angle(v_1, v_2) - np.pi / 2.) < MACHINE_PRECISION)

        v_1 = [0, 1]
        v_2 = [1, 0]
        self.assertTrue(abs(calculate_angle(v_1, v_2)) < MACHINE_PRECISION)

        v_1 = [0, 1]
        v_2 = [-1, 0]
        self.assertTrue(abs(calculate_angle(v_1, v_2)) < MACHINE_PRECISION)

        v_1 = [1, 1]
        v_2 = [1, 0]
        self.assertTrue(abs(calculate_angle(v_1, v_2) - np.pi/4.) < MACHINE_PRECISION)

        v_1 = [1, -1]
        v_2 = [1, 0]
        self.assertTrue(abs(calculate_angle(v_1, v_2) - np.pi/4.) < MACHINE_PRECISION)

    def test_get_option(self):
        """Testing the getOption() utility method"""

        options = sys.argv = ['--input', 'inputFile']

        self.assertTrue(getOption('input') == 'inputFile', 'Input switch option failed.')

        self.assertFalse(getOption('input') == 'outputFile', 'Input switch option should not return outputFile.')

        self.assertTrue(sys.argv == options, 'System arguments should be correctly passed through to the options.')

    def test_vector2(self):
        """Testing the Vector2 class"""


if __name__ == "__main__":
    unittest.main()
