# Main-Script
# #############################################################################

# This python script can be used to generate a trajectory with constrains from
# a floorplan or similar geometry.

# Authors:
# Christopher Mahn
# Silas Teske
# Joshua Wolf

# #############################################################################

# Import of Libraries
# -----------------------------------------------------------------------------

import main as settings
# import string as st
import random as r
import time
# import re
# from turtle import position
# from scipy import interpolate
from concurrent.futures import process
from turtle import position
import numpy as np
import math as m
# import sys
import os
import matplotlib.pyplot as plt
# from scipy.fft import fft, fftfreq
# from scipy import signal
import multiprocessing as mp
import copy
import lib_trajectory as t

# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information

# Functions
# -----------------------------------------------------------------------------

def __help_generate_trajectory(trajectory):
    trajectory.generate()
    return(trajectory.get(), trajectory.get_garbage())


def create_multiple_trajectories(trajectory, ammount):
    """
    This function takes one trajectory-object with specified parameters and
    generates multiple trajectories from it.

    Args:
        trajectory (trajectory-object): Trajectory-object with specified parameters
        ammount (int): Ammount of trajectories to be generated
    """
    trajectory_objects = []

    # Making multiple copies of the trajectory-object
    for i in range(ammount):
        if(verbose):
            print(f'[INFO][1/2][{i+1}/{ammount}] Copying trajectory', end="\r")
        trajectory_objects.append(copy.deepcopy(trajectory))

    # Processing the generation and retrieval of trajectories in parallel
    if(verbose):
        print(f'[INFO][PARALLEL][2/2] Generating {ammount} trajectories')
        if(ammount >= 10):
            print(f'[WARN] This might take some time to process...')
        elif(ammount >= 50):
            print(f'[DANGER] This might be extremely long to process...')
    processing = mp.Pool()
    trajectories = processing.map(__help_generate_trajectory, trajectory_objects)
    return(trajectories)


def __help_plot_lines_rgb(input):
    t.plot_lines_rgb(lines_red=input["red"], lines_green=input["green"], lines_blue=input["blue"], title=input["title"], filename=input["filename"])
    return(None)


def plot_lines_rgb_multiple(filenames, lines_red=None, lines_green=None, lines_blue=None, titles=None):
    if(verbose):
        print(f'[INFO][PARALLEL] Plotting {len(filenames)} graphs')
    tasks = []
    for i, filename in enumerate(filenames):
        red = None
        green = None
        blue = None
        title = "Line-segments"
        if(lines_red != None):
            red = lines_red[i]
        if(lines_green != None):
            green = lines_green[i]
        if(lines_blue != None):
            blue = lines_blue[i]
        if(titles != None):
            title = titles[i]
        tasks.append({"red": red, "green": green, "blue": blue, "title":title, "filename": filename})
    processing = mp.Pool()
    processing.map(__help_plot_lines_rgb, tasks)
    return(None)


# Classes
# -----------------------------------------------------------------------------

class Trajectory():
    def __init__(self,
                 position_init={"x": 0.0, "y": 0.0},
                 direction_init=0,
                 direction_step_noise=10/180*m.pi,
                 direction_try_noise_add=5/180*m.pi,
                 length_total=250,
                 length_step=0.8,
                 length_step_noise=0.15,
                 geometry=[],
                 trajectory=[],
                 not_trajectory=[],
                 tries=5,
                 check_length_buffer=0.4,
                 check_width_buffer=0.3):
        self.position_init = position_init
        # This is the initial position, where the trajectories are generated 
        # from

        self.direction_init = direction_init
        # This is the initial direction the trajectory starts from

        self.direction_step_noise = direction_step_noise
        # This is the amount of bending, that occurs as a base angle-change.

        self.direction_try_noise_add = direction_try_noise_add
        # This is the amount of bending, that get's applied for areas with
        # higher generation-difficulty.

        self.length_total = length_total
        # length of the trajectory in footsteps

        self.length_step = length_step
        # length of the average footstep in meters

        self.length_step_noise = length_step_noise
        # standard-deviation of the average footstep

        self.geometry = geometry
        # This is a list of Line-Objects, that form a complex boundary for the
        # trajectory

        self.trajectory = trajectory
        # This is a list, which will contain the generated trajectory
        # consisting of line segments.

        self.not_trajectory = not_trajectory
        # This is a list with all Line-segments, that were discarded in the
        # trajectory-generation.

        self.tries = tries
        # This variable sets the number of tries a step will be generated,
        # before stepping back one step recursively.

        self.check_length_buffer = check_length_buffer
        # This variable controls the behaviour for the trajectory to avoid
        # direct wall-contact. The step will be extended by this amount in
        # meters before checking intersection with walls.

        self.check_width_buffer = check_width_buffer
        # This variable controls the behaviour for the trajectory to avoid
        # direct wall-contact. The step will be widened by this amount in
        # meters before checking intersection with walls.

    def __copy__(self):
        return(type(self)(self.position_init,
                          self.direction_init,
                          self.direction_step_noise,
                          self.direction_try_noise_add,
                          self.length_total,
                          self.length_step,
                          self.length_step_noise,
                          self.geometry,
                          self.trajectory,
                          self.not_trajectory,
                          self.tries,
                          self.check_length_buffer,
                          self.check_width_buffer))

    def __deepcopy__(self, memo):  # I don't know what memo is for, but it's
                                   # something with recursive copy or something
                                   # similar
        return(type(self)(
               copy.deepcopy(self.position_init, memo), 
               copy.deepcopy(self.direction_init, memo), 
               copy.deepcopy(self.direction_step_noise, memo), 
               copy.deepcopy(self.direction_try_noise_add, memo), 
               copy.deepcopy(self.length_total, memo), 
               copy.deepcopy(self.length_step, memo), 
               copy.deepcopy(self.length_step_noise, memo), 
               copy.deepcopy(self.geometry, memo), 
               copy.deepcopy(self.trajectory, memo), 
               copy.deepcopy(self.not_trajectory, memo), 
               copy.deepcopy(self.tries, memo), 
               copy.deepcopy(self.check_length_buffer, memo), 
               copy.deepcopy(self.check_width_buffer, memo)))

    def export(self):
        return(self.position_init,
               self.direction_init,
               self.direction_step_noise,
               self.direction_try_noise_add,
               self.length_total,
               self.length_step,
               self.length_step_noise,
               self.geometry,
               self.trajectory,
               self.not_trajectory,
               self.tries,
               self.check_length_buffer,
               self.check_width_buffer)

    def set_start_coordinate(self, x, y):
        self.position_init["x"] = float(x)
        self.position_init["y"] = float(y)

    def set_start_direction(self, direction):
        self.direction_init = float(direction)

    def set_direction_turn_noise(self, mdev):
        self.direction_step_noise = float(mdev)

    def set_trajectory_length(self, footsteps):
        self.length_total = float(footsteps)

    def set_median_step_size(self, length):
        self.length_step = float(length)

    def set_step_size_noise(self, mdev):
        self.length_step_noise = float(mdev)

    def set_geometry(self, line_segments):
        self.geometry = line_segments

    def __check_intersection(self, line):
        """
        This method checks if a line is intersecting with some of the internal geometry.

        Args:
            line (Line-Object): This line will be checked against the geometry.
        """
        intersection = False
        point1 = {"x": line.x1(), "y": line.y1()}
        point2 = {"x": line.x2(), "y": line.y2()}
        for i in self.geometry:
            point3 = {"x": i.x1(), "y": i.y1()}
            point4 = {"x": i.x2(), "y": i.y2()}
            try:
                intersected_point = t.geradenschnitt(point1, point2, point3, point4)
                if(point1["x"] <= intersected_point["x"] <= point2["x"] and point3["x"] <= intersected_point["x"] <= point4["x"]):
                    intersection = True
                elif(point1["x"] >= intersected_point["x"] >= point2["x"] and point3["x"] <= intersected_point["x"] <= point4["x"]):
                    intersection = True
                elif(point1["x"] <= intersected_point["x"] <= point2["x"] and point3["x"] >= intersected_point["x"] >= point4["x"]):
                    intersection = True
                elif(point1["x"] >= intersected_point["x"] >= point2["x"] and point3["x"] >= intersected_point["x"] >= point4["x"]):
                    intersection = True
            except(Exception):
                pass
                # if(verbose):
                #     print(f'[WARN] intersection could not be calculated')
            if(intersection):
                break
        return(intersection)

    def generate_legacy(self):
        """
        This method generates the trajectory using a iterative aproach.
        """
        direction = self.direction_init
        position = self.position_init
        self.trajectory = []
        for i in range(self.length_total):
            tries = 0
            direction_try = direction
            while(tries < 100):
                # print(f'{tries}    ', end="\r")
                direction_try += np.random.normal(0, self.direction_step_noise)
                length_try = self.length_step + np.random.normal(0, self.length_step_noise)
                position_try = {"x": None, "y": None}
                position_try["x"] = position["x"] + (m.cos(direction_try) * length_try)
                position_try["y"] = position["y"] + (m.sin(direction_try) * length_try)
                line_try = t.Line(position["x"], position["y"], position_try["x"], position_try["y"])
                if(self.__check_intersection(line_try)):
                    tries += 1
                else:
                    self.trajectory.append(line_try)
                    direction = direction_try
                    position = position_try
                    break

    def generate(self):
        """
        This function generates the trajectory recursively.
        """
        direction = [self.direction_init]
        position = [self.position_init]
        self.trajectory = []
        tries = [0]
        while(len(position) <= self.length_total):
            if(verbose):
                # print(f'[INFO][{len(position)+1}/{self.length_total}] Generating trajectory ', end="\r")
                pass
            while(tries[-1] < self.tries):
                tries[-1] += 1
                direction_try = np.random.normal(direction[-1], (self.direction_step_noise + (tries[-1] * self.direction_try_noise_add)))
                length_try = np.random.normal(self.length_step, self.length_step_noise)

                # Line-segment for the trajectory
                position_try = {"x": None, "y": None}
                position_try["x"] = position[-1]["x"] + (m.cos(direction_try) * length_try)
                position_try["y"] = position[-1]["y"] + (m.sin(direction_try) * length_try)
                line_try = t.Line(position[-1]["x"], position[-1]["y"], position_try["x"], position_try["y"])

                # Line-segments for the Intersection-Check
                position_check1_1 = {"x": None, "y": None}
                position_check1_2 = {"x": None, "y": None}
                position_check2_1 = {"x": None, "y": None}
                position_check2_2 = {"x": None, "y": None}
                position_check1_1["x"] = position[-1]["x"] + (m.cos(direction_try - (90/180*m.pi)) * (self.check_width_buffer))
                position_check1_1["y"] = position[-1]["y"] + (m.sin(direction_try - (90/180*m.pi)) * (self.check_width_buffer))
                position_check1_2["x"] = position_check1_1["x"] + (m.cos(direction_try) * (length_try + self.check_length_buffer))
                position_check1_2["y"] = position_check1_1["y"] + (m.sin(direction_try) * (length_try + self.check_length_buffer))
                position_check2_1["x"] = position[-1]["x"] + (m.cos(direction_try + (90/180*m.pi)) * (self.check_width_buffer))
                position_check2_1["y"] = position[-1]["y"] + (m.sin(direction_try + (90/180*m.pi)) * (self.check_width_buffer))
                position_check2_2["x"] = position_check2_1["x"] + (m.cos(direction_try) * (length_try + self.check_length_buffer))
                position_check2_2["y"] = position_check2_1["y"] + (m.sin(direction_try) * (length_try + self.check_length_buffer))
                line_check_1 = t.Line(position_check1_1["x"], position_check1_1["y"], position_check1_2["x"], position_check1_2["y"])
                line_check_2 = t.Line(position_check2_1["x"], position_check2_1["y"], position_check2_2["x"], position_check2_2["y"])
                line_check_3 = t.Line(position_check1_1["x"], position_check1_1["y"], position_check2_1["x"], position_check2_1["y"])
                line_check_4 = t.Line(position_check1_1["x"], position_check1_1["y"], position_check2_2["x"], position_check2_2["y"])

                # Intersection-Check and Saving if Line-Segments
                if(self.__check_intersection(line_check_1) or
                   self.__check_intersection(line_check_2) or
                   self.__check_intersection(line_check_3) or
                   self.__check_intersection(line_check_4)):
                    pass
                else:
                    direction.append(direction_try)
                    position.append(position_try)
                    tries.append(0)
                    self.trajectory.append(line_try)
                    if(len(self.trajectory) > self.length_total):
                        break
            direction.pop(-1)
            position.pop(-1)
            tries.pop(-1)
            self.not_trajectory.append(self.trajectory.pop(-1))

    def get(self):
        # This method returns the trajectory
        return(self.trajectory)

    def get_garbage(self):
        # This method returns the line-segments, that failed to generate
        return(self.not_trajectory)

# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':

    # Setting starting values
    start_positions = settings.project_start_positions
    start_directions = settings.project_start_directions
    
    # Collecting all plot-data for later parallel processing
    plots = {"filenames": [], "lines_red": [], "lines_green": [], "lines_blue": [], "titles": []}

    # Iterating over all projects, do ...
    for index, projectname in enumerate(settings.project_filenames):

        # Import floorplan
        floorplan = t.lines_import(f'{projectname}_lines.csv')

        # Set up the trajectory
        trajectory = Trajectory()
        trajectory.set_geometry(floorplan)
        trajectory.set_start_coordinate(start_positions[index]["x"], start_positions[index]["y"])
        trajectory.set_start_direction(start_directions[index])

        # Creating the trajectories
        data = create_multiple_trajectories(trajectory, settings.trajectories_per_project)

        # Saving the data
        trajectories = []
        not_trajectories = []
        for i in data:
            trajectories.append(i[0])
            not_trajectories.append(i[1])
        del i
        
        # Iterating over the individual trajectories, do ...
        for trajectory_index, current_trajectory in enumerate(trajectories):
            
            # Export the trajectory as .csv-file
            t.lines_export(current_trajectory, f'trajectory_{projectname}_{trajectory_index+1:05d}_ground-truth.csv')

            # Create Plot 1
            plots["filenames"].append(f'trajectory_{projectname}_{trajectory_index+1:05d}')
            plots["titles"].append(f'Trajectory with floorplan "{projectname}"')
            plots["lines_red"].append(None)
            plots["lines_green"].append(current_trajectory)
            plots["lines_blue"].append(floorplan)

            # Create Plot 2
            plots["filenames"].append(f'trajectory_{projectname}_{trajectory_index+1:05d}_with_disregarded_lines')
            plots["titles"].append(f'Trajectory with floorplan "{projectname}" and discarded Line-segments')
            plots["lines_red"].append(not_trajectories[trajectory_index])
            plots["lines_green"].append(current_trajectory)
            plots["lines_blue"].append(floorplan)

    # Plotting everything in parallel
    plot_lines_rgb_multiple(filenames=plots["filenames"],
                            lines_red=plots["lines_red"],
                            lines_green=plots["lines_green"],
                            lines_blue=plots["lines_blue"],
                            titles=plots["titles"])
