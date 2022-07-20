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

import math as m
# import string as st
# import random as r
# import re
import os
import platform

from sklearn import datasets


# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# -----------------------------------------------------------------------------
# Project-Settings

project_filenames = ["floor_EG", "floor_1OG", "floor_4OG"]
project_start_positions = [{"x": 5932827, "y": 566527},
                           {"x": 5932836, "y": 566560},
                           {"x": 5932823, "y": 566526}]
project_start_directions = [80/180*m.pi, 80/180*m.pi, 80/180*m.pi]
trajectories_per_project = 1
datasets_per_trajectory = 5


# Functions
# -----------------------------------------------------------------------------

def __run_script(script_name):
    """
    This function executes python scripts via the command line.

    Args:
        script_name (str): name of the python script (eg: "demo.py")
    """
    if(platform.system() == "Linux"):
        if(verbose):
            print(f'[INFO] Executing "{script_name}" as Linux-User')
        os.system(f'python3 {script_name}')  # Run on Linux
    elif(platform.system() == "Windows"):
        if(verbose):
            print(f'[INFO] Executing "{script_name}" as Windows-User')
        user = os.environ.get('USERNAME')
        os.system(f'C:/Users/{user}/anaconda3/python.exe {script_name}')  # Run on Windows


# Classes
# -----------------------------------------------------------------------------


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    __run_script("prepare_data.py")
    __run_script("generate_trajectory.py")
    __run_script("noising_trajectory.py")
    __run_script("linear_regression.py")
