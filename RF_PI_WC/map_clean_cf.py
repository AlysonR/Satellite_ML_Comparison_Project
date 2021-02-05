import numpy as np
import sys
import grid_from_lat_lon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import cmap
from skimage.metrics import structural_similarity as ssim

brmap = cmap.get_rbluemap()
warm_dict = np.load('PIAI_12.npy', allow_pickle = True, encoding = 'bytes').item()
model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
model_names = ['Random Forest', 'SGB', 'MVLR', 'XGBoost']
regions = warm_dict[models[0]].keys()
areas = [str(b)[2:-1] for b in regions]

clean_cf = {}
for model in models:
	clean_cf[model] = []
for model in models:
	for area in regions:
		
		clean_cf[model].append(np.nanmean(warm_dict[model][area][b'clean_cf']) * 100)


for i, model in enumerate(clean_cf.keys()):
	
	grid, lats, lons = grid_from_lat_lon.make_grid(clean_cf[model], areas)
	
	m = Basemap(projection = 'cyl', llcrnrlat=-90,urcrnrlat=90,  llcrnrlon=-180, urcrnrlon=180, resolution = 'c')
	m.fillcontinents(color = '#005C1F', lake_color = '#005C1F')
	m.drawcoastlines()
	
	parallels = [-60, 0, 60]
	m.drawparallels(parallels, labels = [True for p in parallels], dashes = [100, .000001], fontsize = 18)
	
	meridians = [-180, -90, 0, 90, 180]
	m.drawmeridians(meridians, labels = [True for b in meridians], dashes = [100,.0000001], fontsize = 18)
	
	plt.pcolormesh(lons, lats, grid, cmap = brmap, norm = cmap.MidpointNormalize(midpoint=0.), vmin = 0, vmax = 100)
	plt.title('{}\n'.format(model_names[i]), weight = 'semibold', size = 24, color = model_colors[i])
	plt.subplots_adjust(left = .07, top = .85)
	print(round(np.nanmean(grid), 1))
	ticks = [0, 25, 50, 75, 100]
	cbar = plt.colorbar( fraction = .07, pad = .08)
	cbar.ax.tick_params(labelsize = 18)
	cbar.set_label('Simulated Pristine Cloud Fraction', size = 20)
	plt.show()


	
