import numpy as np
import grid_from_lat_lon
import sys
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
sys.path.append('/home/users/rosealyd/ML_sat_obs/daily/')
import get_day
import get_year
import pickle
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.pyplot as plt

regime_list = ['#f55742', '#b89537', '#fff940', '#92db00', '#346332', '#7affc8',
'#ffa500', '#3497d9', '#193778', '#9485e6', '#8935bd', '#b82c84', '#f5aec4']

mean = True
std = False
assert(mean == True or std == True), 'mean or std must be True'
map_regime = False
bar_chart = False
map_grid = False
features = ['EIS', 'sst', 'RH700', 'AOD','Ang', 'V_250', 'w500', 'evap']

#lwp is called cwp in daily
variable = 'cwp'
N = 2
n_regimes = 13
with open('/home/users/rosealyd/ML_sat_obs/ML_models/clusters/sc_{}_{}.pickle'.format(N, n_regimes), 'rb' ) as f:
	t = pickle.load(f)
	labels, areas, importances = t[0], t[1], t[2]

if bar_chart:
	bar_dict = {}
	importances = np.array(importances)
	for n in range(int(n_regimes)):
		label_mask = (np.array(labels) == n)
		imp_n = importances[label_mask]
		bar_dict[n] = {}
		bar_dict[n]['mean'] = np.nanmean(imp_n, axis = 0)
		bar_dict[n]['std'] = np.std(imp_n, axis = 0)
		plt.subplot(3, 5, n+1)
		xt = np.linspace(0, 10, importances.shape[1])
		plt.bar(xt, bar_dict[n]['mean'], color = regime_list[n], width = 1.)
		yt = np.linspace(0, .35, 5)
		plt.yticks(ticks = yt, labels = ['{}%'.format(int(y * 100)) for y in yt])
		plt.xticks(xt, labels = features, rotation = 45)
	plt.subplots_adjust(hspace = .4, wspace = .4, top = .99, left = .04, right = .99)
	plt.show()
	

labels_masks = {}

grid, lats, lons = grid_from_lat_lon.make_grid(labels, areas, res = N)
if map_grid:
	tempmap = LinearSegmentedColormap.from_list('regimes', regime_list[:n_regimes], N = n_regimes)
	plt.pcolormesh(lons, lats, grid, cmap = tempmap)
	plt.colorbar()
	plt.show()
	sys.exit()
#analyze_dict = get_year.get_vars_in_N_grid([variable], range(2003, 2016), N = N)
analyze_dict = get_day.get_vars_in_N_grid([variable], range(2003, 2017), N = N)

cluster_dict = {}

grid = np.array(grid)
for label in range(int(n_regimes + 1)):
	
	label_mask = (grid == label)
	print(label_mask.shape)
	cluster_dict[label] = {}
	if mean:
		temp_variable_grid = np.nanmean(analyze_dict[variable], axis = 0)
		cluster_dict[label][variable] = temp_variable_grid[label_mask]
		
	if std:
		temp = []
		temp2 = []
		for year in range(analyze_dict[variable].shape[0]):
			t = analyze_dict[variable][year][label_mask]
			temp.append(np.std(t))
			
		cluster_dict[label][variable] = temp
		
	if map_regime:
		temp_var = analyze_dict[variable][0].copy()
		temp_mask = (grid != label)
		temp_var[temp_mask] = np.nan
		cluster_dict[label]['map'] = temp_var
if map_regime:
	plt.subplot(131)	
	plt.pcolormesh(lons, lats, cluster_dict[8]['map'], vmin = 0, vmax = 1, cmap = 'cividis')
	plt.colorbar()
	plt.subplot(132)
	plt.pcolormesh(lons, lats, cluster_dict[10]['map'], vmin = 0, vmax = 1, cmap = 'cividis')
	plt.colorbar()
	plt.subplot(133)
	plt.pcolormesh(lons, lats, cluster_dict[11]['map'], vmin = 0, vmax = 1, cmap = 'cividis')
	plt.colorbar()
	plt.show()
	
	

for n in [8, 10, 11]:
	print(n)
	plt.hist(cluster_dict[n][variable], bins = np.linspace(30, 400, 40), color = regime_list[n], lw = 3.5, histtype = 'step', weights = [1./len(cluster_dict[n][variable]) for p in cluster_dict[n][variable]])
	
	mean = np.nanmean(cluster_dict[n][variable])
	plt.plot([mean, mean], [0, .3], '--', c = regime_list[n], lw = 3)
	
	plt.xticks(size = 14)
	yts = np.linspace(0, .3, 5)
	plt.yticks(yts, ['{}%'.format(int(y * 100)) for y in yts], size = 14)
	plt.xlabel('Liquid Water Path', size = 20)
	plt.ylim(0, .3)
plt.show()

	
	
	
