#!/usr/bin/env python
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import json
from pylab import rcParams
import sys

rcParams['figure.figsize'] = 19.5,10 #width, height

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))
def map_grid(grid, lats, lons, title = ''):
	m = Basemap(projection = 'cyl', llcrnrlat=-90,urcrnrlat=90,  llcrnrlon=-180, urcrnrlon=180, resolution = 'c')
	m.fillcontinents(color = '#005C1F', lake_color = '#005C1F')
	m.drawcoastlines()
	parallels = [-60, 0, 60]
	m.drawparallels(parallels, labels = [True for p in parallels], dashes = [100, .000001], fontsize = 14)
	meridians = [-180, -90, 0, 90, 180]
	m.drawmeridians(meridians, labels = [True for b in meridians], dashes = [100,.0000001], fontsize = 14)

	plt.pcolormesh(lons, lats, grid, cmap = plt.cm.get_cmap('tab10', 4))
	plt.title(title + '\n', size = 24)
	
	plt.show()
	return
	










