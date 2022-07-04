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

# import string as st
# import random as r
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


# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------

def geradenschnitt(punkt1, punkt2, punkt3, punkt4):
    """
    Diese Funktion berechnet einen Geradenschnitt zwischen der Geraden von
    Punkt 1 zu Punkt 2 und der Geraden von Punkt 3 zu Punkt 4.
    Die Punkt werden jeweils in folgendem Format übergeben:
    punkt1 = {"x": FLOAT, "y": FLOAT}
    punkt2 = {"x": FLOAT, "y": FLOAT}
    punkt3 = {"x": FLOAT, "y": FLOAT}
    punkt4 = {"x": FLOAT, "y": FLOAT}
    """
    t12 = (punkt2["y"]-punkt1["y"])/(punkt2["x"]-punkt1["x"])
    t34 = (punkt4["y"]-punkt3["y"])/(punkt4["x"]-punkt3["x"])
    xs = punkt3["x"]
    xs += (((punkt3["y"]-punkt1["y"])-(punkt3["x"]-punkt1["x"])*t12)/(t12-t34))
    ys = punkt1["y"]+(xs-punkt1["x"])*t12
    punkt5 = {"y": ys, "x": xs}
    return(punkt5)


def import_lines(filename):
    if(verbose):
        print(f'[Info] Importing file "{filename}"', end="\r")
    with open(os.path.join("data", filename)) as file:
        data = np.loadtxt(file, delimiter=";")
    lines = []
    for entry in data:
        lines.append(Line(entry[0], entry[1], entry[2], entry[3]))
    if(verbose):
        print(f'[Info] Imported file "{filename}" successfully')
    return(lines)


def plot_line_segments(line_segments, title):
    for i in line_segments:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()])
    # plt.legend(["lines"])
    plt.grid()
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title(title)
    plt.show()


def plot_results(datasets, title_label, x_label, y_label, data_label, timestamps=None):
    """
    This function plots graphs.

    Args:
        datasets ([[float]]): A list with datasets a lists with floating-point
        
                              numbers
        title_label (str): This is the tile of the plot
        x_label (str): This is the label of the x-axis
        y_label (str): This is the label of the y-axis
        data_label ([str]): This is a list with labels of the datasets
        timestamps ([float], optional): By using a list of floating-point
                                        numbers the data get's plotted on a
                                        time-axis. If nothing is provided the
                                        values will be plotted equidistant.
    """
    for i, dataset in enumerate(datasets):
        if(timestamps==None):
            timestamps = range(len(dataset))
        plt.plot(timestamps, dataset)
    plt.legend(data_label)
    plt.grid()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title_label)
    plt.show()


def plot_geometry(geometry1, title):
    for i in geometry1:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()], color='blue')
    plt.grid()
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title(title)
    plt.show()


def plot_two_geometries(geometry1, geometry2, title):
    for i in geometry1:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()], color='blue')
    for i in geometry2:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()], color='green')
    plt.grid()
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title(title)
    plt.show()


def plot_three_geometries(geometry1, geometry2, geometry3, title):
    for i in geometry1:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()], color='blue')
    for i in geometry2:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()], color='green')
    for i in geometry3:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()], color='red')
    plt.grid()
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title(title)
    plt.show()


def line_segments_to_points(line_segments):
    points = {"x": [], "y": []}
    points["x"].append(line_segments[0].x1())
    points["y"].append(line_segments[0].y1())
    for line in line_segments:
        points["x"].append(line.x2())
        points["y"].append(line.y2())
    return(points)


def generate_trajectory(trajectory):
    trajectory.generate()
    return(trajectory.get())


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
        print(f'[INFO][{i+1}/{ammount}] Generating multiple trajectories', end="\r")
        trajectory_objects.append(copy.copy(trajectory))

    # Processing the gerneration and retrieval of trajectories in parallel
    processing = mp.Pool()
    trajectories = processing.map(generate_trajectory, trajectory_objects)
    return(trajectories)


def write_trajectory(points, filename):
    """
    This function takes a list of points and writes them to a text-file.

    Args:
        points ({"x": [float], "y": [float]}): A list of points formated in a dictionary
        filename (str): the filename where the points are written to
    """
    with open(os.path.join("data", filename), "w") as f:
        for i, x in enumerate(points["x"]):
            f.write(f'{x}, {points["y"][i]}\n')
    return(None)


# Classes
# -----------------------------------------------------------------------------

class Trajectory():
    def __init__(self):
        self.__position_init = {"x": 0.0, "y": 0.0}
        # This is the initial position, where the trajectories are generated 
        # from

        self.__direction_init = 0
        # This is the initial direction the trajectory starts from

        self.__direction_step_noise = 10/180*m.pi
        # This is the amount of bending, that occurs as a base angle-change.

        self.__direction_try_noise_add = 5/180*m.pi
        # This is the amount of bending, that get's applied for areas with
        # higher generation-difficulty.

        self.__length_total = 250
        # length of the trajectory in footsteps

        self.__length_step = 0.8
        # length of the average footstep in meters

        self.__length_step_noise = 0.15
        # standard-deviation of the average footstep

        self.__geometry = []
        # This is a list of Line-Objects, that form a complex boundary for the
        # trajectory

        self.__trajectory = []
        # This is a list, which will contain the generated trajectory
        # consisting of line segments.

        self.__not_trajectory = []
        # This is a list with all Line-segments, that were discarded in the
        # trajectory-generation.

        self.__tries = 5
        # This variable sets the number of tries a step will be generated,
        # before stepping back one step recursively.

        self.__check_length_buffer = 0.4
        # This variable controls the behaviour for the trajectory to avoid
        # direct wall-contact. The step will be extended by this amount in
        # meters before checking intersection with walls.

        self.__check_width_buffer = 0.3
        # This variable controls the behaviour for the trajectory to avoid
        # direct wall-contact. The step will be widened by this amount in
        # meters before checking intersection with walls.

    def set_start_coordinate(self, x, y):
        self.__position_init["x"] = float(x)
        self.__position_init["y"] = float(y)

    def set_start_direction(self, direction):
        self.__direction_init = float(direction)

    def set_direction_turn_noise(self, mdev):
        self.__direction_step_noise = float(mdev)

    def set_trajectory_length(self, footsteps):
        self.__length_total = float(footsteps)

    def set_median_step_size(self, length):
        self.__length_step = float(length)

    def set_step_size_noise(self, mdev):
        self.__length_step_noise = float(mdev)

    def set_geometry(self, line_segments):
        self.__geometry = line_segments

    def __check_intersection(self, line):
        """
        This method checks if a line is intersecting with some of the internal geometry.

        Args:
            line (Line-Object): This line will be checked against the geometry.
        """
        intersection = False
        point1 = {"x": line.x1(), "y": line.y1()}
        point2 = {"x": line.x2(), "y": line.y2()}
        for i in self.__geometry:
            point3 = {"x": i.x1(), "y": i.y1()}
            point4 = {"x": i.x2(), "y": i.y2()}
            try:
                intersected_point = geradenschnitt(point1, point2, point3, point4)
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
        direction = self.__direction_init
        position = self.__position_init
        self.__trajectory = []
        for i in range(self.__length_total):
            tries = 0
            direction_try = direction
            while(tries < 100):
                # print(f'{tries}    ', end="\r")
                direction_try += np.random.normal(0, self.__direction_step_noise)
                length_try = self.__length_step + np.random.normal(0, self.__length_step_noise)
                position_try = {"x": None, "y": None}
                position_try["x"] = position["x"] + (m.cos(direction_try) * length_try)
                position_try["y"] = position["y"] + (m.sin(direction_try) * length_try)
                line_try = Line(position["x"], position["y"], position_try["x"], position_try["y"])
                if(self.__check_intersection(line_try)):
                    tries += 1
                else:
                    self.__trajectory.append(line_try)
                    direction = direction_try
                    position = position_try
                    break
            if(verbose):
                print(f'[INFO][{i+1}/{self.__length_total}] Generating trajectory', end="\r")

    def generate(self):
        """
        This function generates the trajectory recursively.
        """
        direction = [self.__direction_init]
        position = [self.__position_init]
        self.__trajectory = []
        tries = [0]
        while(len(position) <= self.__length_total):
            if(verbose):
                # print(f'[INFO][{len(position)+1}/{self.__length_total}] Generating trajectory   ', end="\r")
                pass
            while(tries[-1] < self.__tries):
                tries[-1] += 1
                direction_try = np.random.normal(direction[-1], (self.__direction_step_noise + (tries[-1] * self.__direction_try_noise_add)))
                length_try = np.random.normal(self.__length_step, self.__length_step_noise)

                # Line-segment for the trajectory
                position_try = {"x": None, "y": None}
                position_try["x"] = position[-1]["x"] + (m.cos(direction_try) * length_try)
                position_try["y"] = position[-1]["y"] + (m.sin(direction_try) * length_try)
                line_try = Line(position[-1]["x"], position[-1]["y"], position_try["x"], position_try["y"])

                # Line-segments for the Intersection-Check
                position_check1_1 = {"x": None, "y": None}
                position_check1_2 = {"x": None, "y": None}
                position_check2_1 = {"x": None, "y": None}
                position_check2_2 = {"x": None, "y": None}
                position_check1_1["x"] = position[-1]["x"] + (m.cos(direction_try - (90/180*m.pi)) * (self.__check_width_buffer))
                position_check1_1["y"] = position[-1]["y"] + (m.sin(direction_try - (90/180*m.pi)) * (self.__check_width_buffer))
                position_check1_2["x"] = position_check1_1["x"] + (m.cos(direction_try) * (length_try + self.__check_length_buffer))
                position_check1_2["y"] = position_check1_1["y"] + (m.sin(direction_try) * (length_try + self.__check_length_buffer))
                position_check2_1["x"] = position[-1]["x"] + (m.cos(direction_try + (90/180*m.pi)) * (self.__check_width_buffer))
                position_check2_1["y"] = position[-1]["y"] + (m.sin(direction_try + (90/180*m.pi)) * (self.__check_width_buffer))
                position_check2_2["x"] = position_check2_1["x"] + (m.cos(direction_try) * (length_try + self.__check_length_buffer))
                position_check2_2["y"] = position_check2_1["y"] + (m.sin(direction_try) * (length_try + self.__check_length_buffer))
                line_check_1 = Line(position_check1_1["x"], position_check1_1["y"], position_check1_2["x"], position_check1_2["y"])
                line_check_2 = Line(position_check2_1["x"], position_check2_1["y"], position_check2_2["x"], position_check2_2["y"])
                line_check_3 = Line(position_check1_1["x"], position_check1_1["y"], position_check2_1["x"], position_check2_1["y"])
                line_check_4 = Line(position_check1_1["x"], position_check1_1["y"], position_check2_2["x"], position_check2_2["y"])

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
                    self.__trajectory.append(line_try)
                    if(len(self.__trajectory) > self.__length_total):
                        break
            direction.pop(-1)
            position.pop(-1)
            tries.pop(-1)
            self.__not_trajectory.append(self.__trajectory.pop(-1))
            """
            if(len(self.__not_trajectory)%1000 == 0):
                for i in range(50):
                    direction.pop(-1)
                    position.pop(-1)
                    tries.pop(-1)
                    self.__not_trajectory.append(self.__trajectory.pop(-1))
                    """

    def get(self):
        return(self.__trajectory)

    def get_garbage(self):
        return(self.__not_trajectory)


class Line():
    def __init__(self, x1, y1, x2, y2):
        self.__x1 = float(x1)
        self.__y1 = float(y1)
        self.__x2 = float(x2)
        self.__y2 = float(y2)

    def x1(self):
        return(self.__x1)

    def y1(self):
        return(self.__y1)

    def x2(self):
        return(self.__x2)

    def y2(self):
        return(self.__y2)


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    filenames = ["EG_polygon_semantic_edited_converted.csv", "1OG_polygon_semantic_edited_converted.csv", "4OG_polygon_semantic_edited_converted.csv"]
    start_positions = [{"x": 5932827, "y": 566527},
                       {"x": 5932836, "y": 566560},
                       {"x": 5932823, "y": 566526}]
    for index, filename in enumerate(filenames):
        lines = import_lines(filename)
        trajectory = Trajectory()
        trajectory.set_geometry(lines)
        # plot_geometry(lines, "Floorplan")
        trajectory.set_start_coordinate(start_positions[index]["x"], start_positions[index]["y"])
        trajectory.set_start_direction(80/180*m.pi)
        trajectories = create_multiple_trajectories(trajectory, 20)
        # plot_line_segments(trajectory.get(), "Trajectory")
        for i, current_trajectory in enumerate(trajectories):
            points = line_segments_to_points(current_trajectory)
            write_trajectory(points, f'trajectory_{filename[0:-4]}_{i+1:05d}.csv')
            # plot_results([points["x"]],
            #             "Trajektorie",
            #             "Y",
            #             "X",
            #             ["Trajektorie"],
            #             points["y"])
            # plot_two_geometries(lines, current_trajectory, f'Trajectory with floorplan "{filename}"')
            # plot_three_geometries(lines, current_trajectory, trajectory.get_garbage(), f'Trajectory with floorplan "{filename}"')
