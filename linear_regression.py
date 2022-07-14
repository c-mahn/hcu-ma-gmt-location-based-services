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
import noising_trajectory as nt

from sklearn.linear_model import LinearRegression as lr

# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------


def linear_regression(trajectory_measured, trajectory_groundtruth):
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
            trajectory_measured = nt.import_trajectory(f'{dataset}_noised_{trajectory_index+1:05d}.csv')
            trajectory_ground_truth = nt.import_trajectory(f'{dataset}_{trajectory_index+1:05d}.csv')
