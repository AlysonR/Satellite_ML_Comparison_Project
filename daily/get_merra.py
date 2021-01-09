import glob
import numpy as np
import sys
from netCDF4 import Dataset
import daily_tools
import matplotlib.pyplot as plt


merra_dir = '/gws/nopw/j04/eo_shared_data_vol1/reanalysis/MERRA-2/'

onedeg_lats = np.arange(-89.5, 90.5, 1)
onedeg_lons = np.arange(-179.5, 180.5, 1)

def get_daily(year, month, day, modis_lats, modis_lons):
	merra_filename = merra_dir + '{}_{}_{}.npy'.format(day, month, year)
	print(merra_filename)
	
	daily_merra = np.load(merra_filename, allow_pickle = True).item()
	#print(daily_merra.keys())
	
	merra_lats = daily_merra.pop('lats')
	
	merra_lons = daily_merra.pop('lons')
	
	for key in daily_merra.keys():
		temp_mean = np.array(daily_merra[key])
		temp_mean[np.isnan(temp_mean)] = 0.
		daily_merra[key] = daily_tools.interp(temp_mean, merra_lats, merra_lons, modis_lats, modis_lons)
		daily_merra[key][(daily_merra[key] == 0.)] = np.nan
		daily_merra[key] = np.flip(daily_merra[key], axis = 0)
	return daily_merra
