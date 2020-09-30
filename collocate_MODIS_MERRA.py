import numpy as np
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import load_l2_MODIS
import datetime
import glob
import copy

merra_dir = '/gws/nopw/j04/eo_shared_data_vol1/reanalysis/MERRA-2/'

modis_day = '002'
modis_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd06_l2/2007/{}/'

merra_hours = np.array([0, 6, 12, 18, 24])

#first get the modis data
modis_daily = glob.glob(modis_dir.format(modis_day) + '*.hdf')
modis_dict = {}
for filename in modis_daily:
	warm_frac, all_frac, lat_lon_dict = load_l2_MODIS.get_cloud_fraction(filename, average = True, local_grid = True, local_space = 2.5)
	modis_lats = [(l1 + l2)/2 for l1, l2 in zip(lat_lon_dict['lats'][:-1], lat_lon_dict['lats'][1:])]
	modis_lons = [(l1 + l2)/2 for l1, l2 in zip(lat_lon_dict['lons'][:-1], lat_lon_dict['lons'][1:])]
	
	hour = int(filename.split('/')[-1].split('.')[2][:2])
	#minute = filename.split('/')[-1].split('.')[2][2:]
	corr_merra_t = np.abs(merra_hours - hour).argmin()
	if corr_merra_t == 4:
		modis_day = int(modis_day) + 1
		corr_merra_t = 0
	date = datetime.date(2007, 1, 1) + datetime.timedelta(days = int(modis_day) -1)
	merra_filename = merra_dir + date.strftime('%d_%m_%Y.npy')
	merra_data = np.load(merra_filename).item()
	
	print('creating tree')
	X = []
	merra_idxs = []
	for i, lat in enumerate(merra_data['lats']):
		for j, lon in enumerate(merra_data['lons']):
			X.append(np.array([lat, lon]))
			merra_idxs.append([i, j])
	X = np.array(X)
	
	merra_kdtree = KDTree(X)
	lts_grid = copy.deepcopy(warm_frac)
	for i in range(len(warm_frac)):
		for j in range(len(warm_frac[i])):
			test = np.array([np.array([modis_lats[i], modis_lons[j]])])
			d, idx = merra_kdtree.query(test)
			merra_point = X[idx[0]][0]
			merra_x = list(merra_data['lats']).index(merra_point[0])
			merra_y = list(merra_data['lons']).index(merra_point[1])
			lts_grid[i][j] = merra_data['EIS'][corr_merra_t][merra_x][merra_y]
			
	
	plt.subplot(131)
	plt.title('LTS')
	plt.pcolormesh(lts_grid)
	plt.colorbar()
	plt.subplot(132)
	plt.title('All CF')
	plt.pcolormesh(all_frac, vmin = 0, vmax = 1.)
	plt.colorbar()
	plt.subplot(133)
	plt.title('Warm CF')
	plt.pcolormesh(warm_frac, vmin = 0, vmax = 1.)
	plt.show()
	break
