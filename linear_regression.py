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
# from scipy import interpolate
# from concurrent.futures import process
# from turtle import position
import numpy as np
import math as m
# import sys
import os
# import matplotlib.pyplot as plt
# from scipy.fft import fft, fftfreq
# from scipy import signal
# import multiprocessing as mp
# import copy
import generate_trajectory as gt

from sklearn.linear_model import LinearRegression as lr

# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------

def import_noised_trajectory(filename):
    """
    This function imports simple trajectories, that are represented as a list
    of Line-objects.

    Args:
        filename ("str"): name of the file, where the trajectory is saved in
    """
    if(verbose):
        print(f'[Info] Importing file "{filename}"')
    with open(os.path.join("data", filename)) as file:
        data = np.loadtxt(file, delimiter=";")
    trajectory = []
    for i in data:
        trajectory.append(i[0], gt.Line(i[1], i[2], i[3], i[4]), i[5], i[6], i[7], i[8], i[9])
    return(trajectory)

def import_raw_trajectory(filename):
    """
    This function imports simple trajectories, that are represented as a list
    of Line-objects.

    Args:
        filename ("str"): name of the file, where the trajectory is saved in
    """
    if(verbose):
        print(f'[Info] Importing file "{filename}"')
    with open(os.path.join("data", filename)) as file:
        data = np.loadtxt(file, delimiter=";")
    trajectory = []
    for i in data:
        trajectory.append(i[0], gt.Line(i[1], i[2], i[3], i[4]), i[5], i[6], i[7], i[8], i[9])
    return(trajectory)

def linear_regression(trajectory):
    """
    This function applies the linear regression machine learning to the noise of the synthetic measurements.

    Args:
        trajectory ([[float, float]]): Trajectory consisting of points
                                       represented as list-entries with two
                                       float-values inside
    """
    for i, point in enumerate(trajectory):
        if(verbose):
            print(f'[INFO][{i+1}/{len(trajectory)}] Applying linear regression to the noise of the trajectory', end="\r")
        
    if(verbose):
        print("")
    return()

# Classes
# -----------------------------------------------------------------------------


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Dataset-Information
    datasets = ["trajectory_EG_polygon_semantic_edited_converted",
                "trajectory_1OG_polygon_semantic_edited_converted",
                "trajectory_4OG_polygon_semantic_edited_converted"]
    dataset_lengths = [10, 10, 10]
    
    # Import of individual trajectories
    for dataset_index, dataset in enumerate(datasets):
        dataset_length = dataset_lengths[dataset_index]
        for trajectory_index in range(dataset_length):
            trajectory = import_noised_trajectory(f'{dataset}_noised_{trajectory_index+1:05d}.csv')
            trajectory = import_raw_trajectory(f'{dataset}_{trajectory_index+1:05d}.csv')
