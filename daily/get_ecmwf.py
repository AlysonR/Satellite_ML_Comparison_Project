import numpy as np
import glob
from netCDF4 import Dataset
import sys
import daily_tools
import matplotlib.pyplot as plt

def get_ecmwf(year, month, day):
	directory = '/badc/ecmwf-era-interim/data/gg/fs/{}/{}/{}/'.format(year, month, day)
	
	modis_lats = np.arange(-89.5, 90.5, 1)
	modis_lons = np.arange(-179.5, 180.5, 1)
	
	daily_cape = []
	daily_t2 = []
	for filename in glob.glob(directory + '*.nc'):
		cape_data = Dataset(filename, 'r')
		lats = cape_data['latitude'][:].astype(float)
		lons = cape_data['longitude'][:].astype(float) - 180.
		cape = cape_data['CAPE'][:][0, 0, :, :]
		t2m = cape_data['T2'][:][0, 0, :, :]
		daily_t2.append(t2m)
		daily_cape.append(cape)
	
	daily_cape = np.nanmean(daily_cape, axis = 0)
	daily_t2 = np.nanmean(daily_t2, axis = 0)
	
	daily_t2 = daily_tools.interp(daily_t2, lats, lons, modis_lats, modis_lons)
	bad = (daily_t2 > 360)
	daily_t2[bad] = np.nan
	daily_t2 = np.flip(daily_t2, axis = 0)
	
	daily_cape = daily_tools.interp(daily_cape, lats, lons, modis_lats, modis_lons)
	bad = (daily_cape > 2e9)
	daily_cape[bad] = np.nan
	daily_cape = np.flip(daily_cape, axis = 0)
	
	return daily_cape, daily_t2

	
get_ecmwf(2007, '01', '01')
