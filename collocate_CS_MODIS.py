#!usr/bin/env python
import sys
import numpy as np
import copy
import datetime
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import src


	
diy = 57
year = 2008

print 'getting MODIS grids for ', diy, year

modis_dict = src.get_modis_lls(diy, year)

print 'getting cloudsat lats/lons'
X = src.get_cs(diy, year)

print 'building tree'
tree = KDTree(X)

for modis_filename, grid_dict in modis_dict.iteritems():
	print 'doing', modis_filename
	modis_lats = grid_dict['lats']
	modis_lons = grid_dict['lons']
	indices_modis = []
	distances = []
	indices_cloudsat = []
	
	lats_cloudsat = []
	lats_modis = []
	
	print 'finding indices'
	for n in range(len(modis_lats)):
		#contains the distance, index of X, modis lat lon, modis indices, and cloudsat lat lons
		dis_idx_mll_midx_csll = []
		for i, ll in enumerate(zip(modis_lats[n], modis_lons[n])):
			
			distance, index = tree.query([ll])
			csll = X[index[0][0]]
			
			dis_idx_mll_midx_csll.append((distance[0][0], index[0][0], ll, (n, i), csll))
		min_d = min(dis_idx_mll_midx_csll)
		print min_d[2], min_d[-1]
		indices_modis.append(min_d[3])
		indices_cloudsat.append(index[0][0])
		distances.append(min_d[0])
	
		lats_cloudsat.append(min_d[-1][0])
		lats_modis.append(min_d[2][0])
	plt.plot(distances)
	plt.show()
	plt.plot(lats_modis, lats_cloudsat)
	plt.show()




