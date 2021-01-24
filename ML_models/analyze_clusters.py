import numpy as np
import grid_from_lat_lon
import sys
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year

import matplotlib.pyplot as plt

mean = False
std = True

[labels, areas] = np.load('current_regimes.npy')
num_labels = int(max(labels))
labels_masks = {}

grid, lats, lons = grid_from_lat_lon.make_grid(labels, areas)
grid = np.array(grid)

analyze_dict = get_year.get_vars_in_grid(['cf', 'lwp'], range(2003, 2016))

if mean:
	analyze_dict['cf'] = np.nanmean(analyze_dict['cf'], axis = 0)
	analyze_dict['lwp'] = np.nanmean(analyze_dict['lwp'], axis = 0)

cluster_dict = {}
for label in range(num_labels):
	#temp_cf = analyze_dict['cf'][0].copy()
	#temp_mask = (grid != label)
	#temp_cf[temp_mask] = np.nan
	label_mask = (grid == label)
	cluster_dict[label] = {}
	if mean:
		cluster_dict[label]['cf'] = analyze_dict['cf'][label_mask]
		cluster_dict[label]['lwp'] = analyze_dict['lwp'][label_mask]
	if std:
		temp = []
		for year in range(analyze_dict['cf'].shape[0]):
			t = analyze_dict['cf'][year][label_mask]
			temp.append(np.std(t))
		cluster_dict[label]['cf'] = temp

for n in cluster_dict.keys():
	plt.hist(cluster_dict[n]['cf'], histtype = 'step')
plt.show()

	
	
	
