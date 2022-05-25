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
# import math as m
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
        self.__position = {"x": 0.0, "y": 0.0}
        self.__direction = 0
        self.__total_length = 100

    def set_start_coordinate(self, x, y):
        self.__position["x"] = float(x)
        self.__position["x"] = float(y)

    def set_start_direction(self, direction):
        self.__direction = float(direction)

    def set_trajectory_length(self, footsteps):
        self.__total_length = float(footsteps)


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    pass
