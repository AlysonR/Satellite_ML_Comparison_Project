#!usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import glob
import sys

#Assumes 15 x 15

lat = np.linspace(-90, 90, 181)
lon = np.linspace(-180, 180, 361)

def get_lat_indices(c_l):
	global lat
	lat_index = next((x[0] for x in enumerate(lat) if x[1] > c_l), -1)-1
	return lat_index
	
def get_lon_indices(c_l):
	global lon
	lon_index = next((x[0] for x in enumerate(lon) if x[1] > c_l), -1)-1
	return lon_index
	
	
def make_grid(values, cases):
	global lat, lon
	v_lats = [float(c.split('_')[0]) for c in cases]
	v_lons = [float(c.split('_')[1]) for c in cases]
	
	calc_lat_indices = np.vectorize(get_lat_indices)
	calc_lon_indices = np.vectorize(get_lon_indices)

	lon_indices = calc_lon_indices(v_lons)
	lat_indices = calc_lat_indices(v_lats)
	
	grid = [[np.nan for i in range(len(lon)-1)] for j in range(len(lat)-1)]

	
	for lo_i, la_i, v in zip(lon_indices, lat_indices, values):
		grid[la_i][lo_i] = v
	
	return grid, lat, lon

