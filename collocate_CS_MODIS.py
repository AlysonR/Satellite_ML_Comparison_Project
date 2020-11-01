#!usr/bin/env python
import sys
import numpy as np
import copy
import glob
from datetime import timedelta
import datetime
from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF, HC
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import cloudsat_tools


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
cloudsat_files = [sorted(glob.glob(cloudsat_dir.format(year, day_before) + '*.hdf'))[-1]]
cloudsat_day_of = sorted(glob.glob(cloudsat_dir.format(year, diy) + '*.hdf'))
cloudsat_files.extend(cloudsat_day_of)
#note: cloudsat filenames go year, day, HH MM SS at the start

#chunk cloudsat by 5 minutes
cloudsat_chunks = {}
for cloudsat_granule in cloudsat_files:
	print(cloudsat_granule)
	cloudsat_data = HDF(cloudsat_granule, HC.READ)
	time = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Profile_time')]
	granule_time = cloudsat_granule.split('/')[-1].split('_')[0]
	start_time = datetime.datetime(year = int(granule_time[:4]), month = 1, day = 1, hour = int(granule_time[7:9]), minute = int(granule_time[9:11]))
	start_time += datetime.timedelta(days = int(granule_time[4:7]))
	time = [start_time + datetime.timedelta(seconds = int(a)) for a in time]
	start_chunk = start_time.replace(minute = start_time.minute - start_time.minute%5, second = 0)
	end_chunk = time[-1].replace(minute = (start_time.minute - start_time.minute%5) + 5, second = 0)
	num_chunks = int((end_chunk - start_chunk).seconds/300)
	five_min_intervals = [start_chunk + datetime.timedelta(minutes = 5 * i) for i in range(num_chunks +1)]
	#find where cloudsat times ~ 5 minute interval +- 2 seconds
	
	cs_lats = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Latitude')]
	cs_lons = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Longitude')]
	
	
	sys.exit()


print('getting MODIS files as X')
for filename in modis_files:
	print(filename)
	modis_locs_data = SD(filename, SDC.READ)
	modis_latitudes = modis_locs_data.select('Latitude')
	modis_longitudes = modis_locs_data.select('Longitude')
	
	sys.exit()











