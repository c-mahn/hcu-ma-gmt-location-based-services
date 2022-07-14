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
    """
    This function scales a trajectory with a mean and standard deviation.

    Args:
        trajectory ([Line]): The trajectory consisting of Line-objects in a list.
        mean (float): The mean scaling factor for each step.
        stdev (float): the standard deviation for the scaling factor of each step.
    """
    if(verbose):
        print(f'[INFO] Scaling trajectory')
    trajectory_new = []
    while(trajectory != []):
        # Selecting and scaling one line at a time
        current_line = trajectory.pop(0)
        current_scale = np.random.normal(mean, stdev)
        trajectory_new.append(gt.Line(current_line.x1(),
                                      current_line.y1(),
                                      current_line.x1() + (current_line.delta_x()*current_scale),
                                      current_line.y1() + (current_line.delta_y()*current_scale)))
        delta_x = (current_line.x1() + (current_line.delta_x()*current_scale)) - current_line.x2()
        delta_y = (current_line.y1() + (current_line.delta_y()*current_scale)) - current_line.y2()

        # Scaling the rest of the lines attached to the current line
        if(trajectory != []):
            for index, line in enumerate(trajectory):
                trajectory[index] = gt.Line(line.x1()+delta_x,
                                            line.y1()+delta_y,
                                            line.x2()+delta_x,
                                            line.y2()+delta_y)
    return(trajectory_new)


def rotate_trajectory(trajectory, mean, stdev):
    """
    This function rotates a trajectory with a mean and standard deviation.

    Args:
        trajectory ([Line]): The trajectory consisting of Line-objects in a list.
        mean (float): The mean rotation factor for each step.
        stdev (float): the standard deviation for the rotation factor of each step.
    """
    if(verbose):
        print(f'[INFO] Rotating trajectory')
    trajectory_new = []
    while(trajectory != []):
        # Selecting and rotating one line at a time
        current_line = trajectory.pop(0)
        current_rotation = np.random.normal(mean, stdev)
        trajectory_new.append(gt.Line(current_line.x1(),
                                      current_line.y1(),
                                      current_line.x1()+(m.cos(current_line.direction()+current_rotation)*current_line.length()),
                                      current_line.y1()+(m.sin(current_line.direction()+current_rotation)*current_line.length())))
        delta_x = trajectory_new[-1].x2()-current_line.x2()
        delta_y = trajectory_new[-1].y2()-current_line.y2()

        # Scaling the rest of the lines attached to the current line
        if(trajectory != []):
            for index, line in enumerate(trajectory):
                trajectory[index] = gt.Line(line.x1()+delta_x,
                                            line.y1()+delta_y,
                                            line.x1()+delta_x+m.cos(line.direction()+current_rotation)*line.length(),
                                            line.y1()+delta_y+m.sin(line.direction()+current_rotation)*line.length())
                delta_x = (line.x1()+delta_x+m.cos(line.direction()+current_rotation)*line.length())-line.x2()
                delta_y = (line.y1()+delta_y+m.sin(line.direction()+current_rotation)*line.length())-line.y2()
    return(trajectory_new)


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
            
            trajectory = scale_trajectory(trajectory, step_length_scale, step_length_noise)
            trajectory = rotate_trajectory(trajectory, rotation_drift, rotation_noise)
            gt.write_trajectory(trajectory, f'{dataset}_noised_{trajectory_index+1:05d}.csv')
