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

# These settings affect how the executed scripts below will compute the data.
# Changing these values may increase execution-time significantly or allowes to
# change the computed input or output.

project_filenames = ["floor_EG", "floor_1OG", "floor_4OG"]
# These are the project-names for each "room"/floorplan where trajectories are
# generated inside.

project_start_positions = [{"x": 5932827, "y": 566527},
                           {"x": 5932836, "y": 566560},
                           {"x": 5932823, "y": 566526}]
# These are the starting-positions for the trajectories inside the
# project-environments.

project_start_directions = [80/180*m.pi, 80/180*m.pi, 80/180*m.pi]
# These are the starting-directions for the startpoint for the trjectories,
# that are going to be generated.

trajectories_per_project = 1
# The ammount of trajectories per project controls the ammount of trajectories,
# that are going to be generated per project. Having 3 projects with 4
# trajectories per project will result in 12 trajectories with each floorplan
# having 4.

datasets_per_trajectory = 5
# This variable controlls how many noised trajectories are going to be
# generated for each trajectory. When having 12 trajectories from the previous
# step and setting this variable to 10 would result in a total of 120
# trajectories on top of the existing 12 trajectories, but having bias and
# noise with the direction and length of the steps. The last trajectory, that
# is going to be generated will not be used as training, but rather as
# validation afterwards.


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
