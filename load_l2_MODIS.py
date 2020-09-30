import glob
import numpy as np
from pyhdf.SD import SD, SDC
import sys
import matplotlib.pyplot as plt
import copy
from scipy import interpolate


def interp(data, start_lat, start_lon, end_lat, end_lon):
	function = interpolate.interp2d(start_lon, start_lat, data, kind = 'linear')
	new_data = function(end_lon, end_lat)
	return new_data

def get_1deg_modis_lls(filename):
	level_1_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd03/{}/'
	temp = filename.split('/')[-1].split('.')[1]
	year = temp[1:5]
	diy = temp[-3:]
	time = filename.split('/')[-1].split('.')[2]
	
	l1_filename = glob.glob(level_1_dir.format(year) + diy + '/' + 'MYD03.*' + time + '.061*.hdf')[0]
	
	data = SD(l1_filename, SDC.READ)
	lats = data.select('Latitude').get()
	lons = data.select('Longitude').get()
	return lats, lons
	
	
#default is 10 x 10 degrees
default_grid = {'lats': np.linspace(-90, 90, 19), 'lons': np.linspace(-180, 180, 37)}

def assign_lat_idx(c_l):
	lat_index = next((x[0] for x in enumerate(default_grid['lats']) if x[1] > c_l), -1)-1
	if lat_index >= 0:
		return lat_index
	else:
		return -1

def assign_lon_idx(c_l):
	lon_index = next((x[0] for x in enumerate(default_grid['lons']) if x[1] > c_l), -1)-1
	if lon_index >= 0:
		return lon_index
	else:
		return -1



def convert_to_byte(byte_value):
	return str(format(abs(byte_value), '08b'))

def get_L2_data(filename):
	
	#need the 1 km lats/lons
	#latitudes, longitudes = get_1deg_modis_lls(filename)

	level_data = SD(filename, SDC.READ)
	
	lat_5km, lon_5km = level_data.select('Latitude').get(), level_data.select('Longitude').get()
	
	
	re = level_data.select('Cloud_Effective_Radius').get()
	lwp = level_data.select('Cloud_Water_Path').get()/1000.
	cth = level_data.select('Cloud_Top_Height').get()/1000.
	
	ctt = level_data.select('Cloud_Top_Temperature').get() - level_data.select('Cloud_Top_Temperature').attributes()['add_offset'] 
	ctt = ctt * level_data.select('Cloud_Top_Temperature').attributes()['scale_factor']
	
	#ctt = interp(ctt, lat_5km, lon_5km, latitudes, longitudes)
	
	cold = (ctt < 253)
	warm = (ctt > 253)
	
	clear = (cth <= 0)
	cloudy = (cth > 0)
	
	warm_cloud_flag = copy.deepcopy(ctt)
	warm_cloud_flag[cold] = 0.
	warm_cloud_flag[warm] = 1.
	warm_cloud_flag[clear] = 0.
	
	cloud_flag = copy.deepcopy(cth)
	cloud_flag[clear] = 0.
	cloud_flag[cloudy] = 1.
	
	
	N_wc_pixels = np.count_nonzero(warm_cloud_flag)
	N_cloudy_pixels = np.count_nonzero(cloud_flag)
	N_pixels = float(ctt.shape[0] * ctt.shape[1])
	
	#gives the swath cloud fraction
	warm_cloud_fraction = N_wc_pixels/N_pixels
	cloud_fraction = N_cloudy_pixels/N_pixels
	
	
	return re, lwp, cth, ctt, lat_5km, lon_5km, warm_cloud_flag, cloud_flag

def get_cloud_fraction(filename, grid = None, average = False, local_grid = False, local_space = 5.):
	global default_grid
	#first set the grid
	if grid:
		default_grid = grid
	
	#get the warm cloud and cloudy pixels and lls
	_, _, _, _, lats, lons, w_cs, cs = get_L2_data(filename)
	
	if local_grid:
		latitudes = np.arange(np.amin(lats), np.amax(lats), local_space)
		longitudes = np.arange(np.amin(lons), np.amax(lons), local_space)
		default_grid = {'lats': latitudes, 'lons': longitudes}
	
	#place lls in grid
	find_lats = np.vectorize(assign_lat_idx)
	find_lons = np.vectorize(assign_lon_idx)
	
	lat_idxs = find_lats(lats)
	lon_idxs = find_lons(lons)
	
	#create grids based on given info
	wc_grid = [ [ [] for i in range(len(default_grid['lons']))] for j in range(len(default_grid['lats']))]
	c_grid = copy.deepcopy(wc_grid)
	
	#assign flag values to grid cells to find each grid cell's CF
	for i in range(len(lat_idxs)):
		for j in range(len(lat_idxs[0])):
			try:
				wc_grid[lat_idxs[i][j]][lon_idxs[i][j]].append(w_cs[i][j])
				#c_grid[lat_idxs[i][j]][lon_idxs[i][j]].append(cs[i][j])
			except IndexError:
				print(wc_grid[lat_idxs[i][j]][lon_idxs[i][j]])
				print(i, j, w_cs[i][j])
				print(lats[i][j], lons[i][j])
				print(lat_idxs[i][j], lon_idxs[i][j])
				print('here at index error')
				sys.exit()
	
	if average:
		for i in range(len(wc_grid)):
			for j in range(len(wc_grid[0])):
				if len(wc_grid[i][j]) > 0:
					wc_grid[i][j] = np.nanmean(wc_grid[i][j])
				else:
					wc_grid[i][j] = 0.
	
	
	return np.array(wc_grid), np.array(c_grid), default_grid
test_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd06_l2/2007/213/'







