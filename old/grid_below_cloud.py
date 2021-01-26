#!usr/bin/env python
import numpy as np
import pickle
import matplotlib.pyplot as plt
import glob
import sys


def get_lat_indices(c_l):
	lat_index = next((x[0] for x in enumerate(lat) if x[1] > c_l), -1)-1
	return lat_index
	
def get_lon_indices(c_l):
	lon_index = next((x[0] for x in enumerate(lon) if x[1] > c_l), -1)-1
	return lon_index
	
def between_granules(files, lower, upper):
	search_files = [f.replace(root_dir, '').replace('/','') for f in files]
	lower = search_files.index(lower)
	upper = search_files.index(upper)
	return files[lower:upper + 1]
	

calc_lat_indices = np.vectorize(get_lat_indices)
calc_lon_indices = np.vectorize(get_lon_indices)

lat = np.linspace(-60, 60, 121)
lon = np.linspace(-180, 180, 361)
grid = [[[] for i in range(len(lon)-1)] for j in range(len(lat)-1)]


#open the file and calc below cloud cooling
#example file
root_dir = '/thermal/data/Aerosols/warm_rain/'
files = sorted(glob.glob(root_dir + '*'))
folders = between_granules(files, '22678', '23969')
print len(folders)
#August 2007 06718
#October 2007 08015
#August 2008 12050
#October 2008 13335
#August 2009 17366
#October 2009 18652
#August 2010 22678
#October 2010 23969

for granule in folders:
	for filename in glob.glob(granule + '/*.txt'):
		with open(filename, 'r') as f:
			temp = pickle.load(f)

		if all(temp['lats']) > -60 and all(temp['lats']) < 60:

			profile = np.transpose(np.array(temp['lh']))
			below_cloud_cooling = 0
			size = profile.shape[1]

			cooling = []
			for i in range(len(profile[0])):
				aslice = profile[:,i]
				#cloud base is where it first becomes positive
				cloud_base = next((a[0] for a in enumerate(aslice) if a[1] > 0), -1)
				cooling.append(np.sum(aslice[:cloud_base]))
	
	
			#assign to a gridbox

			lat_indices = calc_lat_indices(temp['lats'])
			lon_indices = calc_lon_indices(temp['lons'])
			for point in range(len(cooling)):
				try:
				
					grid[lat_indices[point]][lon_indices[point]].append(cooling[point])
				except IndexError:
					print filename, point, temp['lats'], temp['lons']
					print lat_indices, lon_indices
np.save('2010', grid)
