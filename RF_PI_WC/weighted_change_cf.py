import numpy as np
import sys
import grid_from_lat_lon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import cmap

brcmap = cmap.get_cmap()
warm_dict = np.load('PIAI_12.npy', allow_pickle = True, encoding = 'bytes').item()

weights_dict = np.load('del_ai_weights.npy', allow_pickle = True, encoding = 'bytes').item()
surface_areas = np.load('areas.npy', allow_pickle = True, encoding = 'bytes').item()

model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
model_names = ['Random Forest', 'SGB', 'MVLR', 'XGBoost']
regions = warm_dict[models[0]].keys()
areas = [str(b)[2:-1] for b in regions]

differences = {}
weights_local = []
forcings = []

for model in models:
	differences[model] = []
for model in models:
	for area in regions:
		differences[model].append(np.nanmean(warm_dict[model][area][b'values']))

for area in regions:
	forcings.append(np.nanmean(warm_dict[model][area][b'swf']))
	weights_local.append(warm_dict[model][area][b'length'])
	
weights_local = np.array(weights_local)/np.nansum(weights_local)		
for i, model in enumerate(differences.keys()):
	
	grid, lats, lons = grid_from_lat_lon.make_grid(differences[model], areas)
	wl_grid, _, _ = grid_from_lat_lon.make_grid(weights_local, areas)
	forcings_grid, _, _ = grid_from_lat_lon.make_grid(forcings, areas)
	
	grid = np.array(grid)
	forcings_grid = np.array(forcings_grid) * grid * np.array(wl_grid) * .22
	print(np.nansum(forcings_grid), model)
	
	continue
	m = Basemap(projection = 'cyl', llcrnrlat=-90,urcrnrlat=90,  llcrnrlon=-180, urcrnrlon=180, resolution = 'c')
	m.fillcontinents(color = '#005C1F', lake_color = '#005C1F')
	m.drawcoastlines()
	
	parallels = [-60, 0, 60]
	m.drawparallels(parallels, labels = [True for p in parallels], dashes = [100, .000001], fontsize = 18)
	
	meridians = [-180, -90, 0, 90, 180]
	m.drawmeridians(meridians, labels = [True for b in meridians], dashes = [100,.0000001], fontsize = 18)
	
	plt.pcolormesh(lons, lats, grid, cmap = brcmap, norm = cmap.MidpointNormalize(midpoint=0.), vmin = -3., vmax = 9)
	plt.title(model_names[i] + '\n', weight = 'semibold', size = 24, color = model_colors[i])
	plt.subplots_adjust(left = .07, top = .85)
	
	ticks = [-3., 0, 3, 6, 9]
	cbar = plt.colorbar(ticks = ticks, fraction = .07, pad = .08)
	cbar.ax.tick_params(labelsize = 18)
	cbar.set_label('Change in Cloud Fraction (%)', size = 20)
	plt.show()
	
