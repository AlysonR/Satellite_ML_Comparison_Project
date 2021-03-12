import numpy as np
import sys
import grid_from_lat_lon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import cmap
import math
plt.rcParams["figure.figsize"] = (15, 8)

brcmap = cmap.get_cmap()
warm_dict = np.load('PIAI_96.npy', allow_pickle = True, encoding = 'bytes').item()

weights_dict = np.load('del_ai_weights.npy', allow_pickle = True, encoding = 'bytes').item()
surface_areas = np.load('areas.npy', allow_pickle = True, encoding = 'bytes').item()

model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
model_names = ['Random Forest', 'SGB', 'MVLR', 'XGBoost']
regions = warm_dict[models[0]].keys()
areas = [str(b)[2:-1] for b in regions]
sa_earth = ((6.371 * (10**6))**2) * 4 * math.pi
differences = {}
weights_local = []
forcings = []
sa_area_weight = []
wcf = []
diurnal = []


warm_cloud_freq = np.load('warm_cloud_freq.npy', allow_pickle = True, encoding = 'bytes').item()

for model in models:
	differences[model] = []
for model in models:
	for area in regions:
		differences[model].append(np.nanmean(warm_dict[model][area][b'values']))

for area in regions:
	forcings.append(np.nanmean(warm_dict[model][area][b'swf']))
	weights_local.append(warm_dict[model][area][b'length'])
	lat = int(str(area).split('_')[0][2:])
	sa_area = (math.pi/180.) * ((6.371 * (10**6))**2)
	sa_area *= abs(math.sin(math.radians(lat)) - math.sin(math.radians(lat + 15.)))
	sa_area *= (15.)
	sa_area_weight.append(sa_area)
	wcf.append(warm_cloud_freq[area])
	
sa_area_weight = np.array(sa_area_weight)/sa_earth

weights_local = np.array(weights_local)/np.nansum(weights_local)		
for i, model in enumerate(differences.keys()):
	print(model)
	grid, lats, lons = grid_from_lat_lon.make_grid(differences[model], areas)
	wl_grid, _, _ = grid_from_lat_lon.make_grid(weights_local, areas)
	forcings_grid, _, _ = grid_from_lat_lon.make_grid(forcings, areas)
	sa_area_grid, _, _ = grid_from_lat_lon.make_grid(sa_area_weight, areas)
	wcf_grid, _, _ = grid_from_lat_lon.make_grid(wcf, areas)
	
	grid = np.array(grid) * np.array(wcf_grid) 
	occurrence = grid * np.array(sa_area_grid)
	print(np.nansum(occurrence), 'change cf weighted by occurrence')
	#account for surface area of each box and the diurnal with last two terms
	forcings_grid = np.array(forcings_grid) * grid * np.array(sa_area_grid) * .5
	
	print(np.nansum(forcings_grid), model, 'forcing')
	temp = grid* np.array(sa_area_grid) * 100
	print(np.nansum(temp), model, 'change cf')
	grid = grid * 100
	
	print(np.nanmin(grid), np.nanmax(grid))
	print(np.nanmin(occurrence), np.nanmax(occurrence))
	
	
	m = Basemap(projection = 'cyl', llcrnrlat=-90,urcrnrlat=90,  llcrnrlon=-180, urcrnrlon=180, resolution = 'c')
	m.fillcontinents(color = '#005C1F', lake_color = '#005C1F')
	m.drawcoastlines()
	
	parallels = [-60, 0, 60]
	m.drawparallels(parallels, labels = [True for p in parallels], dashes = [100, .000001], fontsize = 18)
	
	meridians = [-180, -90, 0, 90, 180]
	m.drawmeridians(meridians, labels = [True for b in meridians], dashes = [100,.0000001], fontsize = 18)
	
	min_c = -.02
	max_c = .005
	
	plt.pcolormesh(lons, lats, forcings_grid, cmap = brcmap, norm = cmap.MidpointNormalize(midpoint=0.), vmin = min_c, vmax = max_c)
	plt.title(model_names[i] + '\n', weight = 'semibold', size = 24, color = model_colors[i])
	plt.subplots_adjust(left = .07, top = .85)
	
	ticks = [-.02, -.015, -.01, -.005, 0, .005]
	cbar = plt.colorbar(ticks = ticks, fraction = .07, pad = .08)
	cbar.ax.tick_params(labelsize = 18)
	cbar.set_label('Change in Shortwave Forcing', size = 20)
	plt.show()
	
