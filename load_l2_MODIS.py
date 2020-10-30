import glob
import numpy as np
from pyhdf.SD import SD, SDC
import sys
import matplotlib.pyplot as plt
import copy
from scipy import interpolate

class MissingFileError(Exception):
	"""Base class for missing a MODIS file"""
	pass

def trim_edges_bin(modis_lats, modis_lons, cloud_array, cloud_array2, cloud_array3, cloud_array4):
	
	temp = [[[] for j in range(len(default_grid['lons']))] for i in range(len(default_grid['lats']))]
	temp_2 = copy.deepcopy(temp)
	temp_3 = copy.deepcopy(temp)
	temp_4 = copy.deepcopy(temp)
	
	find_lats = np.vectorize(assign_lat_idx)
	find_lons = np.vectorize(assign_lon_idx)
	for i in range(len(modis_lats)):
		lat_indices = find_lats(modis_lats[i])
		lon_indices = find_lons(modis_lons[i])
		for j, (lai, loi) in enumerate(zip(lat_indices, lon_indices)):
			temp[lai][loi].append(cloud_array[i][j])
			temp_2[lai][loi].append(cloud_array2[i][j])
			temp_3[lai][loi].append(cloud_array3[i][j])
			temp_4[lai][loi].append(cloud_array4[i][j])
			
	
	for i in range(len(temp)):
		temp[i] = [np.nanmean(a) if len(a) > 0 else np.nan for a in temp[i]]
		temp_2[i] = [np.nanmean(a) if len(a) > 0 else np.nan for a in temp_2[i]]
		temp_3[i] = [np.nanmean(a) if len(a) > 0 else np.nan for a in temp_3[i]]
		temp_4[i] = [np.nanmean(a) if len(a) > 0 else np.nan for a in temp_4[i]]
		
	
	temp = np.array(temp)[:-1, :-1]
	temp_2 = np.array(temp_2)[:-1, :-1]
	temp_3 = np.array(temp_3)[:-1, :-1]
	temp_4 = np.array(temp_4)[:-1, :-1]
	
	
	return temp, temp_2, temp_3, temp_4


def interp(data, start_lat, start_lon, end_lat, end_lon):
	function = interpolate.interp2d(start_lon, start_lat, data, kind = 'linear')
	new_data = function(end_lon, end_lat)
	return new_data

def get_1deg_modis_lls(filename):
	parts = filename.split('/')
	time = parts[-1].split('.')[2]
	level_1_dir = '/neodc/modis/data/MYD03/collection61/{}/{}/{}/'
	l1_filename = glob.glob(level_1_dir.format(parts[6], parts[7], parts[8]) + '*.' + time + '.*.hdf')[0]
	
	data = SD(l1_filename, SDC.READ)
	lats = data.select('Latitude').get()
	lons = data.select('Longitude').get()
	return lats, lons
	
	
#default is 10 x 10 degrees
default_grid = {'lats': np.linspace(-90, 90, 19), 'lons': np.linspace(-180, 180, 37)}

def assign_lat_idx(c_l):
	global default_grid
	lat_index = next((x[0] for x in enumerate(default_grid['lats']) if x[1] > c_l), -1)-1
	if lat_index >= 0:
		return lat_index
	else:
		return -1

def assign_lon_idx(c_l):
	global default_grid
	lon_index = next((x[0] for x in enumerate(default_grid['lons']) if x[1] > c_l), -1)-1
	if lon_index >= 0:
		return lon_index
	else:
		return -1



def convert_to_byte(byte_value):
	return str(format(abs(byte_value), '08b'))


#get the 1 km res cloud mask
#find the all cloud CF from this
#use 1, 2 to find twilight CF from this
def get_1km_TW_mask(filename):
	import glob
	modis_mask_dir = '/neodc/modis/data/MYD35_L2/collection61/{}/{}/{}/'
	parts = filename.split('/')
	time = parts[-1].split('.')[2]
	modis_mask_filename = glob.glob(modis_mask_dir.format(parts[6], parts[7], parts[8]) + '*.' + time + '.*.hdf')[0]
	cloud_mask_data = SD(modis_mask_filename, SDC.READ)
	latitudes = cloud_mask_data.select('Latitude').get()
	longitudes = cloud_mask_data.select('Longitude').get()
	cloud_mask = cloud_mask_data.select('Cloud_Mask').get()
	byte_all = np.vectorize(convert_to_byte)
	cloud_mask_converted = byte_all(cloud_mask)
	#00110001
	c_shape = cloud_mask_converted.shape
	cloudy = [[0 for i in range(c_shape[1])] for j in range(c_shape[2])]
	for row in range(len(cloud_mask_converted)):
		for aisle in range(len(cloud_mask_converted[row])):
			for byte in cloud_mask_converted[row][aisle]:
				if str(byte)[1:3] == '01':
					cloudy[row][aisle] = 1.
				else:
					cloudy[row][aisle]= 0.
	cloudy = np.array(cloudy)
	return latitudes, longitudes

def get_L2_data(filename):
	#optinoal to get twilight flag from 1km cloud mask data
	#twilight_flag = get_1km_TW_mask(filename)
	
	lat_1km, lon_1km = get_1deg_modis_lls(filename)
	
	level_data = SD(filename, SDC.READ)
	
	twilight_flag = level_data.select('Cloud_Mask_5km').get().tolist()
	for i in range(len(twilight_flag)):
		for j in range(len(twilight_flag[i])):
			byte = str(convert_to_byte(twilight_flag[i][j][0]))
			if byte[1:3] == '01' or byte[1:3] == '00':
				twilight_flag[i][j] = 1.
			else:	
				twilight_flag[i][j] = 0.			
	lat_5km, lon_5km = level_data.select('Latitude').get(), level_data.select('Longitude').get()
	
	re = level_data.select('Cloud_Effective_Radius').get().astype('float')
	bad_re = (re == -9999.)
	re[bad_re] = np.nan
	re = re - level_data.select('Cloud_Effective_Radius').attributes()['add_offset']
	re = re * level_data.select('Cloud_Effective_Radius').attributes()['scale_factor']
	print(lon_1km.shape, lat_1km.shape)
	plt.subplot(141)
	plt.pcolormesh(lon_1km, lat_1km, re)
	plt.colorbar()
	
	print(re.shape, 're')
	lwp = level_data.select('Cloud_Water_Path').get()/1000.
	print(lwp.shape, 'lwp')
	cth = level_data.select('Cloud_Top_Height').get()/1000.
	print(cth.shape, 'cth')
	
	plt.subplot(142)
	plt.pcolormesh(lon_5km, lat_5km, cth)
	
	ctt = level_data.select('Cloud_Top_Temperature').get() - level_data.select('Cloud_Top_Temperature').attributes()['add_offset'] 
	ctt = ctt * level_data.select('Cloud_Top_Temperature').attributes()['scale_factor']
	
	#ctt = interp(ctt, lat_5km, lon_5km, latitudes, longitudes)
	
	cold = (ctt < 253)
	warm = (ctt > 253)
	
	clear = (cth <= 0)
	nan = np.isnan(cth)
	cloudy = (cth > 0)
	
	warm_cloud_flag = copy.deepcopy(ctt)
	warm_cloud_flag[cold] = 0.
	warm_cloud_flag[warm] = 1.
	warm_cloud_flag[clear] = 0.
	
	cloud_flag = copy.deepcopy(cth)
	cloud_flag[nan] = 0.
	cloud_flag[clear] = 0.
	cloud_flag[cloudy] = 1.
	
	N_wc_pixels = np.count_nonzero(warm_cloud_flag)
	N_cloudy_pixels = np.count_nonzero(cloud_flag)
	N_pixels = float(ctt.shape[0] * ctt.shape[1])
	
	#gives the swath cloud fraction
	warm_cloud_fraction = N_wc_pixels/N_pixels
	cloud_fraction = N_cloudy_pixels/N_pixels
	
	
	return re, lwp, cth, ctt, lat_5km, lon_5km, warm_cloud_flag, cloud_flag, twilight_flag, lat_1km, lon_1km

def get_cloud_fraction(filename, lat_s = .5, lon_s = .5):
	global default_grid
	
	#get the warm cloud and cloudy pixels and lls
	re, lwp, cth, _, lats, lons, w_cs, cs, ts, lats_1km, lons_1km = get_L2_data(filename)
	
	#first set the grid
	
	latitudes = np.arange(np.amin(np.amin(lats)), np.amax(np.amax(lats))+lat_s, lat_s)
	longitudes = np.arange(np.amin(np.amin(lons)), np.amax(np.amax(lons))+lat_s, lon_s)
	default_grid = {'lats': latitudes, 'lons': longitudes}
	
	c_grid, wc_grid, t_grid, cth_grid  = trim_edges_bin(lats, lons, cs, w_cs, ts, cth)
	
	re_grid, lwp_grid, _, _ = trim_edges_bin(lats_1km, lons_1km, re, lwp, re, lwp)
	plt.subplot(143)
	plt.pcolormesh(default_grid['lons'], default_grid['lats'], re_grid)
	plt.subplot(144)
	plt.pcolormesh(default_grid['lons'], default_grid['lats'], c_grid, vmin = 0, vmax = 1, cmap = 'viridis')
	plt.show()
	nan_wc_grid = np.isnan(wc_grid)
	wc_grid[nan_wc_grid] = 0.
	nan_c_grid = np.isnan(c_grid)
	c_grid[nan_c_grid] = 0.
	nan_t_grid = np.isnan(t_grid)
	t_grid[nan_t_grid] = 0.
	nan_re_grid = np.isnan(re_grid)
	re_grid[nan_re_grid] = 0.
	nan_cth_grid = np.isnan(cth_grid)
	cth_grid[nan_cth_grid] = 0.
	
	return wc_grid, c_grid, t_grid, re_grid, cth_grid, default_grid
test_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd06_l2/2007/213/'







