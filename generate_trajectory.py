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
import numpy as np
import math as m
# import sys
import os
import matplotlib.pyplot as plt
# from scipy.fft import fft, fftfreq
# from scipy import signal


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


def plot_geometry(geometry, title):
    for i in geometry:
        plt.plot([i.y1(), i.y2()], [i.x1(), i.x2()])
    # plt.legend(["lines"])
    plt.grid()
    plt.xlabel("Y")
    plt.ylabel("X")
    plt.title(title)
    plt.show()


# Classes
# -----------------------------------------------------------------------------

class Trajectory():
    def __init__(self):
        self.__position_init = {"x": 0.0, "y": 0.0}
        # This is the initial position, where the trajectories are generated 
        # from
        
        self.__position = self.__position_init
        # This position changes during generation of the trajectory and is used
        # for line-generation. You may not change it manually.

        self.__direction_init = 0
        # This is the initial direction the trajectory starts from

        self.__direction_step_noise = 15/180*m.pi
        # This is the amount of bending, that can occur for each point of the
        # trajectory. The measurement is given in radians.

        self.__length_total = 500
        # length of the trajectory in footsteps

        self.__length_step = 0.9
        # length of the average footstep in meters

        self.__length_step_noise = 0.15
        # standard-deviation of the average footstep

        self.__geometry = []
        # This is a list of Line-Objects, that form a complex boundary for the
        # trajectory

        self.__trajectory = []
        # This is a list, which will contain the generated trajectory
        # consisting of line segments.

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

    def generate(self):
        """
        This method generates the trajectory.
        """
        direction = self.__direction_init
        self.__position = self.__position_init
        path = []
        path.append(self.__position_init)
        for i in range(self.__length_total):
            tries = 0
            direction_try = direction + np.random.normal(0, self.__direction_step_noise)
            while(tries < 100):
                # print(f'{tries}    ', end="\r")
                direction_try += np.random.normal(0, self.__direction_step_noise)
                length_try = self.__length_step + np.random.normal(0, self.__length_step_noise)
                position_try = {"x": None, "y": None}
                position_try["x"] = self.__position["x"] + (m.cos(direction_try) * length_try)
                position_try["y"] = self.__position["y"] + (m.sin(direction_try) * length_try)
                line_try = Line(self.__position["x"], self.__position["y"], position_try["x"], position_try["y"])
                if(self.__check_intersection(line_try)):
                    tries += 1
                else:
                    self.__trajectory.append(line_try)
                    direction = direction_try
                    self.__position = position_try
                    break
            if(verbose):
                print(f'[INFO][{i+1}/{self.__length_total}] Generating trajectory', end="\r")

    def get_trajectory(self):
        return(self.__trajectory)


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
    filenames = ["EG_polygon_semantic_converted.csv", "1OG_polygon_semantic_converted.csv", "4OG_polygon_semantic_converted.csv"]
    start_positions = [{"x": 566522, "y": 5932816},
                       {"x": 566511, "y": 5932803},
                       {"x": 566508, "y": 5932802}]
    for index, filename in enumerate(filenames):
        lines = import_lines(filename)
        trajectory = Trajectory()
        trajectory.set_geometry(lines)
        # plot_geometry(lines, "Floorplan")
        trajectory.set_start_coordinate(start_positions[index]["x"], start_positions[index]["y"])
        trajectory.set_start_direction(80/180*m.pi)
        trajectory.generate()
        plot_geometry(trajectory.get_trajectory(), "Trajectory")
        all_geom = []
        for i in trajectory.get_trajectory():
            all_geom.append(i)
        for i in lines:
            all_geom.append(i)
        plot_geometry(all_geom, f'Trajectory with floorplan "{filename}"')
