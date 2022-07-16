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
import lib_trajectory as t
from sklearn.neural_network import MLPRegressor


# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------

def write_text(filename, text):
    """
    This function writes text to a file.

    Args:
        filename (str): Name of the file
        text (str): Future content of the file.
    """
    if(verbose):
        print(f'[INFO] Writing text to "{filename}"')
    with open(os.path.join("data", filename), "w") as f:
        f.write(f'{text}')
    return(None)


# Classes
# -----------------------------------------------------------------------------


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Dataset-Information
    datasets = ["trajectory_floor_EG_lines",
                "trajectory_floor_1OG_lines",
                "trajectory_floor_4OG_lines"]
    dataset_length = 10  # Number of datasets per project-name
    trainingset_length = 10  # Number of training-datasets per trajectory
    
    # Import of individual trajectories
    for dataset_index, dataset in enumerate(datasets):
        for trajectory_index in range(dataset_length):
            trajectory_ground_truth = t.lines_import(f'{dataset}_{trajectory_index+1:05d}.csv')  # Ground truth data for training

            # Importing Training-datasets
            trajectories_measured = []
            for trainingset_index in range(trainingset_length):
                trajectories_measured.append(t.lines_import(f'{dataset}_{trajectory_index+1:05d}_noised_{trainingset_index+1:05d}.csv'))

            # Preparing training-data
            data_groundtruth = []
            data_measured = []
            for trainingset_index in range(trainingset_length-1):
                for measurement_index, gt_line in enumerate(trajectory_ground_truth):
                    data_groundtruth.append([gt_line.x1(),
                                             gt_line.y1(),
                                             gt_line.x2(),
                                             gt_line.y2()])
                    data_measured.append([measurement_index,
                                          trajectories_measured[trainingset_index][measurement_index].x1(),
                                          trajectories_measured[trainingset_index][measurement_index].y1(),
                                          trajectories_measured[trainingset_index][measurement_index].x2(),
                                          trajectories_measured[trainingset_index][measurement_index].y2(),
                                          trajectories_measured[trainingset_index][measurement_index].delta_x(),
                                          trajectories_measured[trainingset_index][measurement_index].delta_y(),
                                          trajectories_measured[trainingset_index][measurement_index].direction(),
                                          trajectories_measured[trainingset_index][measurement_index].length()])
            data_groundtruth = np.array(data_groundtruth)
            data_measured = np.array(data_measured)
            
            # Training ML
            mlpr = MLPRegressor(hidden_layer_sizes=(5, 5), solver='adam', max_iter=50000, verbose=True, random_state=1, learning_rate="adaptive", tol=1e-10)
            mlpr.fit(data_measured, data_groundtruth)
            write_text(f'{dataset}_{trajectory_index+1:05d}_ml-model.txt', mlpr.coefs_)

            # Preparing validation-data
            validation_data = []
            for measurement_index, line in enumerate(trajectories_measured[-1]):
                validation_data.append([measurement_index,
                                        line.x1(),
                                        line.y1(),
                                        line.x2(),
                                        line.y2(),
                                        line.delta_x(),
                                        line.delta_y(),
                                        line.direction(),
                                        line.length()])
            validation_data = np.array(validation_data)
            
            # Validating ML
            ml_prediction = mlpr.predict(validation_data)
            
            # Export Prediction
            predicted_trajectory = []
            for i, e in enumerate(ml_prediction):
                predicted_trajectory.append(t.Line(e[0], e[1], e[2], e[3]))
            t.lines_export(predicted_trajectory, f'{dataset}_{trajectory_index+1:05d}_ml-prediction.txt')
