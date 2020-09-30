import numpy as np
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import load_l2_MODIS
import datetime
import glob

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
	for lat in merra_data['lats']:
		for lon in merra_data['lons']:
			X.append(np.array([lat, lon]))
	X = np.array(X)
	print(X.shape)
	merra_kdtree = KDTree(X)
	modis_points = []
	for i in range(len(warm_frac)):
		for j in range(len(warm_frac[i])):
			modis_points.append(np.array([modis_lats[i], modis_lons[j]]))
			test = np.array([np.array([modis_lats[i], modis_lons[j]])])
			d, idx = merra_kdtree.query(test)
			print(modis_lats[i], modis_lons[j])
			print(X[idx[0]])
			
		break
	break
	
	
