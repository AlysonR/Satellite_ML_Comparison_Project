import numpy as np
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import load_l2_MODIS
import glob
import copy
import get_SST
import sys
import interp_save_MAero
import datetime

class MissingFileError(Exception):
	"""Base class for missing a MODIS file"""
	pass

merra_dir = '/gws/nopw/j04/eo_shared_data_vol1/reanalysis/MERRA-2/'

modis_month = '01'
modis_day = '04'
modis_year = '2007'
modis_dir = '/neodc/modis/data/MYD06_L2/collection61/{}/{}/{}/'

merra_hours = np.array([0, 6, 12, 18, 24])
#first get the modis data
modis_daily = sorted(glob.glob(modis_dir.format(modis_year, modis_month, modis_day) + '*.hdf'))
#interp_save_MAero.get_tiles(modis_daily[:-30])
modis_tomorrow = modis_daily[223:]
modis_daily = modis_daily[:223]
modis_dict = {}

#do this once
ssts, sst_X, sst_latitudes, sst_longitudes = get_SST.find_sst(modis_day, modis_month, modis_year)
print('creating daily sst tree')
sst_kdtree = KDTree(sst_X)

for hour in range(5):
	modis_dict[hour] = []
for filename in modis_daily[20:]:
	print(filename)
	try:
		warm_frac, all_frac, twi_frac, re_mean, cth_mean, lat_lon_dict = load_l2_MODIS.get_cloud_fraction(filename, lat_s = .875, lon_s = .875)
		modis_lats = [(l1 + l2)/2 for l1, l2 in zip(lat_lon_dict['lats'][:-1], lat_lon_dict['lats'][1:])]
		modis_lons = [(l1 + l2)/2 for l1, l2 in zip(lat_lon_dict['lons'][:-1], lat_lon_dict['lons'][1:])]
		
		temp_d = {}
		temp_d['modis_lats'] = lat_lon_dict['lats']
		temp_d['modis_lons'] = lat_lon_dict['lons']
		temp_d['warm_frac'] = warm_frac
		temp_d['all_frac'] = all_frac
		temp_d['twi_frac'] = twi_frac
		temp_d['filename'] = filename
		temp_d['re'] = re_mean
		temp_d['cth'] = cth_mean
		
		hour = int(filename.split('/')[-1].split('.')[2][:2])
		corr_merra_t = np.abs(merra_hours - hour).argmin()
		
		modis_dict[corr_merra_t].append(temp_d)
	except MissingFileError:
		print('Missing a MODIS file for', filename)

for corr_merra_t in modis_dict.keys():
	print(merra_hours[corr_merra_t], 'merra time')
	merra_filename = merra_dir + '{}_{}_{}.npy'.format(modis_day, modis_month, modis_year)
	merra_data = np.load(merra_filename).item()
	print(merra_data.keys())
	print('creating merra tree')
	X = []
	merra_idxs = []
	for i, lat in enumerate(merra_data['lats']):
		for j, lon in enumerate(merra_data['lons']):
			X.append(np.array([lat, lon]))
			merra_idxs.append([i, j])
	X = np.array(X)
	merra_kdtree = KDTree(X)
	
	for number, modis_reading in enumerate(modis_dict[corr_merra_t]):
		tile_name = '{}_{}_{}_{}_{}'.format(number, corr_merra_t, modis_day, modis_month, modis_year)	
		warm_frac = modis_reading['warm_frac']
		modis_lats = [(a + b)/2. for a, b in zip(modis_reading['modis_lats'][:-1], modis_reading['modis_lats'][1:])]
		modis_lons = [(a + b)/2. for a, b in zip(modis_reading['modis_lons'][:-1], modis_reading['modis_lons'][1:])]
		vars_dict = {}
		test = [[0 for i in range(warm_frac.shape[1])] for j in range(warm_frac.shape[0])]
		merra_vars = ['EIS', 'LTS', 'w500', 'u500', 'v500', 'u850', 'v850', 'u700', 'v700', 'RH900', 'RH850', 'RH700', 'evap', 'sens_h', 'latent_h']
		
		for var in merra_vars:
			vars_dict[var] = copy.deepcopy(test)
		
		vars_dict['sst'] = copy.deepcopy(test)
		vars_dict['warm_frac'] = warm_frac
		vars_dict['all_frac'] = modis_reading['all_frac']
		vars_dict['twi_frac'] = modis_reading['twi_frac']
		vars_dict['re'] = modis_reading['re']
		vars_dict['cth'] = modis_reading['cth']
		
		for i in range(len(warm_frac)):
			for j in range(len(warm_frac[i])):
				point = np.array([np.array([modis_lats[i], modis_lons[j]])])
				
				d, idx = merra_kdtree.query(point)
				merra_point = X[idx[0]][0]
				merra_x = list(merra_data['lats']).index(merra_point[0])
				merra_y = list(merra_data['lons']).index(merra_point[1])
				for var in merra_vars:
					vars_dict[var][i][j] = merra_data[var][corr_merra_t][merra_x][merra_y]
				
				_, sst_idx = sst_kdtree.query(point)
				sst_point = sst_X[sst_idx[0]][0]
				sxi = sst_latitudes.index(sst_point[0])
				sxy = sst_longitudes.index(sst_point[1])
				vars_dict['sst'][i][j] = ssts[sxi][sxy]
				
		
		vars_dict['sst'] = np.array(vars_dict['sst'])
		land = (vars_dict['sst'] < 0)
		for var in vars_dict.keys():
			vars_dict[var] = np.array(vars_dict[var])
			vars_dict[var][land] = np.nan
		vars_dict['modis_lats'] = modis_lats
		vars_dict['modis_lons'] = modis_lons
					
			
		np.save('/home/users/rosealyd/ML_sat_obs/cloudy_tiles/' + tile_name, vars_dict)
	
