# Main-Script
# #############################################################################

# This python script automatically launches all other python scripts in the
# right order and computes the entire task.

# Authors:
# Christopher Mahn
# Silas Teske
# Joshua Wolf

# #############################################################################

# Import of Libraries
# -----------------------------------------------------------------------------

# import string as st
# import random as r
# import re
# from turtle import position
# import matplotlib.pyplot as plt
# from scipy import interpolate
# import numpy as np
import math as m
# import sys
# import os
# from scipy.fft import fft, fftfreq
# from scipy import signal


# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------

class Trajectory():
    def __init__(self):
        self.__position_init = {"x": 0.0, "y": 0.0}
        # This is the initial position, where the trajectories are generated
        # from

        self.__direction_init = 0
        # This is the initial direction the trajectory starts from

        self.__direction_step_noise = 30/180*m.pi
        # This is the amount of bending, that can occur for each point of the
        # trajectory. The measurement is given in radians.

        self.__length_total = 100
        # length of the trajectory in footsteps

        self.__length_step = 0.9
        # length of the average footstep in meters

        self.__length_step_noise = 0.15
        # standard-deviation of the average footstep

        self.__geometry = []
        # This is a list of Line-Objects, that form a complex boundary for the
        # trajectory

    def set_start_coordinate(self, x, y):
        self.__position_init["x"] = float(x)
        self.__position_init["x"] = float(y)

    def set_start_direction(self, direction):
        self.__direction_init = float(direction)

    def set_trajectory_length(self, footsteps):
        self.__length_total = float(footsteps)

    def set_median_step_size(self, length):
        self.__length_step = float(length)

    def set_step_size_noise(self, mdev):
        self.__length_step_noise = float(mdev)


class Line():
    def __init__(self, x1, y1, x2, y2):
        self.__x1 = x1
        self.__y1 = y1
        self.__x2 = x2
        self.__y2 = y2


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    pass
