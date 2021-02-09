import numpy as np
from netCDF4 import Dataset
import glob
import sys
import daily_tools
import matplotlib.pyplot as plt

def find_sst(year, month, day, modis_lats, modis_lons):
	modis_lats = np.arange(-89.5, 90.5, 1)
	modis_lons = np.arange(-179.5, 180.5, 1)
	#daily
	if year > 2016:
		sst_dir = '/gws/nopw/j04/cds_c3s_sst/public/data/ICDR_v2/Analysis/L4/v2.0/{}/{}/{}/'.format(year, month, day)
	else:
		sst_dir = '/neodc/esacci/sst/data/gmpe/CDR_V2/L4/v2.0/{}/{}/{}/'.format(year, month, day)
	print(sst_dir)
	filename = glob.glob(sst_dir + '*.nc')[0]
	
	sst_dataset = Dataset(filename, mode = 'r')
	
	#lat, lon, sst
	sst = sst_dataset['analysed_sst'][:][0]
	
	#.25 x .25
	latitudes = sst_dataset['lat'][:]
	longitudes = sst_dataset['lon'][:]
	
	sst = daily_tools.interp(sst, latitudes, longitudes, modis_lats, modis_lons)
	sst[(sst < 240)] = np.nan
	
	return sst
