import glob
import numpy as np
from pyhdf.SD import SD, SDC
import sys
import matplotlib.pyplot as plt
import copy

#default is 10 x 10 degrees
default_grid = {'lats': np.linspace(-60, 60, 13), 'lons': np.linspace(-180, 180, 37)}

def convert_to_byte(byte_value):
	return str(format(abs(byte_value), '08b'))

test_filename = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd06_l2/2007/213/MYD06_L2.A2007213.0125.061.2018042223349.hdf'

def get_L2_data(filename):

	level_data = SD(filename, SDC.READ)
	re = level_data.select('Cloud_Effective_Radius').get()
	lwp = level_data.select('Cloud_Water_Path').get()/1000.
	cth = level_data.select('Cloud_Top_Height').get()/1000.
	
	ctt = level_data.select('Cloud_Top_Temperature').get() - level_data.select('Cloud_Top_Temperature').attributes()['add_offset'] 
	ctt = ctt * level_data.select('Cloud_Top_Temperature').attributes()['scale_factor']

	latitudes = level_data.select('Latitude').get()
	longitudes = level_data.select('Longitude').get()

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
	
	
	return re, lwp, cth, ctt, latitudes, longitudes, warm_cloud_flag, cloud_flag

def get_cloud_fraction(filename, grid = None):
	global default_grid
	#first set the grid
	if not grid:
		grid = default_grid
	#get the warm cloud and cloudy pixels and lls
	_, _, _, _, lats, lons, w_cs, cs = get_L2_data(filename)
	
	#place lls in grid
	
	return

get_cloud_fraction(test_filename)
	






