#!usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import glob
import sys

#Assumes 15 x 15
resolution = 15
lat = np.linspace(-90, 90, int(180/resolution) + 1)
lon = np.linspace(-180, 180, int(360/resolution) + 1)


def get_lat_indices(c_l):
	global lat
	lat_index = next((x[0] for x in enumerate(lat) if x[1] > c_l), -1)-1
	return lat_index
	
def get_lon_indices(c_l):
	global lon
	lon_index = next((x[0] for x in enumerate(lon) if x[1] > c_l), -1)-1
	return lon_index
	
	
def make_grid(values, cases, res = 15):
	global lat, lon, resolution
	resolution = res
	v_lats = [float(c.split('_')[0]) for c in cases]
	v_lons = [float(c.split('_')[1]) for c in cases]
	
	lat = np.linspace(-90, 90, int(180/resolution) + 1)
	lon = np.linspace(-180, 180, int(360/resolution) + 1)
	
	
	calc_lat_indices = np.vectorize(get_lat_indices)
	calc_lon_indices = np.vectorize(get_lon_indices)

	lon_indices = calc_lon_indices(v_lons)
	lat_indices = calc_lat_indices(v_lats)
	
	grid = [[np.nan for i in range(len(lon)-1)] for j in range(len(lat)-1)]

	
	for lo_i, la_i, v in zip(lon_indices, lat_indices, values):
		grid[la_i][lo_i] = float(v)
	
	return grid, lat, lon

