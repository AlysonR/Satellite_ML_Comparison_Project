#!usr/bin/env python
import sys
import numpy as np
import copy
import glob
from datetime import timedelta
import datetime
from pyhdf.SD import SD, SDC
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt


#note this does not take care of the problem of needing leading zeroes on cloudsat diys
	
day = '12'
month = '05'
year = 2008

#note, americans would prefer month day year but for the global good i did day month year
print('getting MODIS grids for ', day, month, year)
modis_dir = '/neodc/modis/data/MOD04_L2/collection61/{}/{}/{}/'
modis_files = sorted(glob.glob(modis_dir.format(year, month, day) + '*.hdf'))
print(modis_files)
print('getting cloudsat lats/lons')
diy = datetime.date(year = year, month = int(month), day = int(day)) - datetime.date(year = year, month = 1, day = 1)
diy = diy.days
day_before = datetime.date(year = year, month = int(month), day = int(day)) - datetime.timedelta(days = 1)
day_before = (day_before - datetime.date(year = year, month = 1, day = 1)).days
print(diy, day_before)
cloudsat_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/cloudsat/2b-geoprof/R05/{}/{}/'
cloudsat_files = sorted(glob.glob(cloudsat_dir.format(year, day_before) + '*.hdf'))
cloudsat_day_of = sorted(glob.glob(cloudsat_dir.format(year, diy) + '*.hdf'))
cloudsat_files.extend(cloudsat_day_of)
#note: cloudsat filenames go year, day, HH MM SS at the start

#chunk cloudsat by 5 minutes
cloudsat_chunks = {}
for cloudsat_granule in cloudsat_files:
	print(cloudsat_granule)
	cloudsat_data = SD(cloudsat_granule, SDC.READ)
	for var in cloudsat_data.datasets():
		print(var)
	sys.exit()


print('getting MODIS files as X')
for filename in modis_files:
	print(filename)
	modis_locs_data = SD(filename, SDC.READ)
	modis_latitudes = modis_locs_data.select('Latitude')
	modis_longitudes = modis_locs_data.select('Longitude')
	
	sys.exit()











