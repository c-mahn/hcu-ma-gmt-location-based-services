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
# import matplotlib.pyplot as plt
# from scipy import interpolate
import numpy as np
import math as m
import json
# import sys
import os
# from scipy.fft import fft, fftfreq
# from scipy import signal


# -----------------------------------------------------------------------------
# Debugging-Settings

verbose = True  # Shows more debugging information


# Functions
# -----------------------------------------------------------------------------

def import_data(input_filename):
    # Import of measurements
    if(verbose):
        print(f'[INFO] Opening file "{input_filename}"', end="\r")
    with open(os.path.join("data", input_filename)) as file:
        if(verbose):
            print(f'[INFO] Reading file "{input_filename}"', end="\r")
        data = file.readlines()
    if(verbose):
        print(f'[INFO] Read file "{input_filename}" successfully')
    text = ""
    for i in data:
        text = f'{text}{i.strip()}'
    return(text)

def convert_walls(geometry):
    coordinates = geometry["coordinates"][0]
    lines = []
    for i, e in enumerate(coordinates):
        lines.append([coordinates[i-1][0], coordinates[i-1][1], e[0], e[1]])
    return(lines)


# Classes
# -----------------------------------------------------------------------------


# Beginning of the Programm
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    filenames = ["EG_polygon_semantic", "1OG_polygon_semantic", "4OG_polygon_semantic", "EG_polygon_semantic_edited", "1OG_polygon_semantic_edited", "4OG_polygon_semantic_edited"]
    for i, filename in enumerate(filenames):
        geometry = []
        data = json.loads(import_data(f'{filename}.geojson'))
        for feature in data["features"]:
            if(feature["properties"]["Type"] == "Wall" or feature["properties"]["Type"] == "Fassade" or feature["properties"]["Type"] == "B_Door" or feature["properties"]["Type"] == "Door" or feature["properties"]["Type"] == "Balcony"):
                if(feature["geometry"] is not None):
                    walls = convert_walls(feature["geometry"])
                    for wall in walls:
                        geometry.append(wall)
        print(f'[INFO] Fetched {len(geometry)} line-segments')
        with open(os.path.join("data", f'{filename}_converted.csv'), "w") as file:
            for j in geometry:
                file.write(f'{j[1]}; {j[0]}; {j[3]}; {j[2]}\n')
