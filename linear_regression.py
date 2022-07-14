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


# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------

def import_trajectory(filename):
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
    lines = []
    for i in data:
        lines.append(gt.Line(i[1], i[2], i[3], i[4]))
    return(lines)


def trajectory_to_lines(trajectory):
    """
    This function converts a 2D trajectory of points into line-segments

    Args:
        trajectory ([[float, float]]): Trajectory consisting of points
                                       represented as list-entries with two
                                       float-values inside
    """
    previous_point = trajectory.pop()
    lines = []
    for i, point in enumerate(trajectory):
        if(verbose):
            print(f'[INFO][{i+1}/{len(trajectory)}] Converting trajectory to line-segments', end="\r")
        lines.append(gt.Line(previous_point[0], previous_point[1], point[0], point[1]))
        previous_point = point
    if(verbose):
        print("")
    return(lines)


def scale_trajectory(trajectory, mean, stdev):
    pass


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
            trajectory = import_trajectory(f'{dataset}_{trajectory_index+1:05d}.csv')
            
            # Generating sensor-noise parameters
            rotation_drift = np.random.normal(0, 0.5/200*m.pi)  # One-sided drift at each step
            rotation_noise = abs(np.random.normal(0, 0.2/200*m.pi))  # Rotation angle noise
            step_length_scale = np.random.normal(1, 0.1)  # Scale of each step
            step_length_noise = abs(np.random.normal(0, 0.025))  # Random scale of each step
            if(verbose):
                print(f'[INFO][CONFIG] Rotation: {rotation_drift:.5f} ± {rotation_noise:.5f} rad, Scale: {step_length_scale:.5f} ± {step_length_noise:.5f} x')
