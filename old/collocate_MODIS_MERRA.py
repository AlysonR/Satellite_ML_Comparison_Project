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
end_day = glob.glob(modis_dir.format(modis_year, modis_month, modis_day) + '*.1830.*.hdf')[0]
end_day = modis_daily.index(end_day)
#interp_save_MAero.get_tiles(modis_daily[:-30])
modis_tomorrow = modis_daily[end_day:]
modis_daily = modis_daily[:end_day]
modis_dict = {}

#do this once
ssts, sst_X, sst_latitudes, sst_longitudes = get_SST.find_sst(modis_day, modis_month, modis_year)
print('creating daily sst tree')
sst_kdtree = KDTree(sst_X)

for hour in range(5):
	modis_dict[hour] = []
for filename in modis_daily:
	print(filename)
	try:
		warm_frac, all_frac, re_mean, cth_mean, sc_mean, sat_pts, lat_lon_dict = load_l2_MODIS.get_cloud_fraction(filename, lat_s = .5, lon_s = .5)
		modis_lats = [(l1 + l2)/2 for l1, l2 in zip(lat_lon_dict['lats'][:-1], lat_lon_dict['lats'][1:])]
		modis_lons = [(l1 + l2)/2 for l1, l2 in zip(lat_lon_dict['lons'][:-1], lat_lon_dict['lons'][1:])]
		
		temp_d = {}
		temp_d['modis_lats'] = lat_lon_dict['lats']
		temp_d['modis_lons'] = lat_lon_dict['lons']
		temp_d['warm_frac'] = warm_frac
		temp_d['all_frac'] = all_frac
		temp_d['filename'] = filename
		temp_d['re'] = re_mean
		temp_d['cth'] = cth_mean
		temp_d['sc_frac'] = sc_mean
		temp_d['sat_pts'] = sat_pts
		
		hour = int(filename.split('/')[-1].split('.')[2][:2])
		corr_merra_t = np.abs(merra_hours - hour).argmin()
		
		modis_dict[corr_merra_t].append(temp_d)
	except MissingFileError:
		print('Missing a MODIS file for', filename)

for corr_merra_t in modis_dict.keys():
	print(merra_hours[corr_merra_t], 'merra time')
	merra_filename = merra_dir + '{}_{}_{}.npy'.format(modis_day, modis_month, modis_year)
	merra_data = np.load(merra_filename, allow_pickle = True).item()
	print('creating merra tree')
	X = []
	merra_idxs = []
	merra_data['lats'] += 90.
	merra_data['lons'] += 180.
	
	for i, lat in enumerate(merra_data['lats']):
		for j, lon in enumerate(merra_data['lons']):
			X.append(np.array([lat, lon]))
			merra_idxs.append([i, j])
	X = np.array(X)
	merra_kdtree = KDTree(X)
	print("done creating tree")
	for number, modis_reading in enumerate(modis_dict[corr_merra_t]):
		tile_name = '{}_{}_{}_{}_{}'.format(number, corr_merra_t, modis_day, modis_month, modis_year)	
		warm_frac = modis_reading['warm_frac']
		vars_dict = {}
		test = [[0 for i in range(warm_frac.shape[1])] for j in range(warm_frac.shape[0])]
		merra_vars = ['EIS', 'LTS', 'w500', 'u500', 'v500', 'u850', 'v850', 'u700', 'v700', 'RH900', 'RH850', 'RH700', 'evap', 'sens_h', 'latent_h']
		#can multiply by airdens to get kg/m3 instead of kg/kg for aerosol species
		aerosol_vars = ['dust', 'hbc', 'pbc', 'dms', 'oc', 'su', 'ss', 'msa', 'airdens']
		aod_vars = ['su_ai', 'su_aod', 'du_ai', 'du_aod', 'oc_ai', 'oc_aod', 'bc_ai', 'bc_aod', 'ss_ai', 'ss_aod', 'tot_ai', 'tot_aod']
		for var in merra_vars:
			vars_dict[var] = copy.deepcopy(test)
		for var in aerosol_vars:
			vars_dict[var] = copy.deepcopy(test)
		for var in aod_vars:
			vars_dict[var] = copy.deepcopy(test)
		modis_lats = modis_reading['modis_lats']
		modis_lons = modis_reading['modis_lons']
		vars_dict['sst'] = copy.deepcopy(test)
		vars_dict['warm_frac'] = warm_frac
		vars_dict['all_frac'] = modis_reading['all_frac']
		vars_dict['re'] = modis_reading['re']
		vars_dict['cth'] = modis_reading['cth']
		vars_dict['sc_frac'] = modis_reading['sc_frac']
		vars_dict['satellite'] = modis_reading['sat_pts']
		for i in range(len(warm_frac)):
			for j in range(len(warm_frac[i])):
				point = np.array([np.array([modis_lats[i], modis_lons[j]])])
				d, idx = merra_kdtree.query(point)
				merra_point = X[idx[0]][0]
				merra_x = list(merra_data['lats']).index(merra_point[0])
				merra_y = list(merra_data['lons']).index(merra_point[1])
				for var in merra_vars:
					vars_dict[var][i][j] = merra_data[var][corr_merra_t][merra_x][merra_y]
				for var in aerosol_vars:
					vars_dict[var][i][j] = merra_data[var][corr_merra_t][merra_x][merra_y]
				for var in aod_vars:
					vars_dict[var][i][j] = merra_data[var][corr_merra_t][merra_x][merra_y]
				
				_, sst_idx = sst_kdtree.query(point)
				sst_point = sst_X[sst_idx[0]][0]
				sxi = sst_latitudes.index(sst_point[0])
				sxy = sst_longitudes.index(sst_point[1])
				vars_dict['sst'][i][j] = ssts[sxi][sxy]
		vars_dict['sst'] = np.array(vars_dict['sst'])
		land_nosat = ((vars_dict['sst'] < 0) | (np.isnan(vars_dict['satellite'])))
		for var in vars_dict.keys():
			vars_dict[var] = np.array(vars_dict[var])
			vars_dict[var][land_nosat] = np.nan
		vars_dict['modis_lats'] = modis_lats
		vars_dict['modis_lons'] = modis_lons
			
		print(tile_name)
		np.save('/home/users/rosealyd/ML_sat_obs/cloudy_tiles/' + tile_name, vars_dict)
	
