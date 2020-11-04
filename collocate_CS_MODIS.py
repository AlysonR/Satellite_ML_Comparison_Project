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
	
day = '21'
month = '05'
year = 2008

#note, americans would prefer month day year but for the global good i did day month year
print('getting MODIS grids for ', day, month, year)
modis_dir = '/neodc/modis/data/MYD35_L2/collection61/{}/{}/{}/'
modis_files = sorted(glob.glob(modis_dir.format(year, month, day) + '*.hdf'))

diy = datetime.date(year = year, month = int(month), day = int(day)) - datetime.date(year = year, month = 1, day = 1)
diy = diy.days
day_before = datetime.date(year = year, month = int(month), day = int(day)) - datetime.timedelta(days = 1)
day_before = (day_before - datetime.date(year = year, month = 1, day = 1)).days

cloudsat_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/cloudsat/2b-geoprof/R05/{}/{}/'
cloudsat_daybefore = sorted(glob.glob(cloudsat_dir.format(year, day_before) + '*.hdf'))[-1]
cloudsat_files = sorted(glob.glob(cloudsat_dir.format(year, diy) + '*.hdf'))
#note: cloudsat filenames go year, day, HH MM SS at the start

#chunk cloudsat by 5 minutes
cloudsat_chunks = {}
for cloudsat_granule in cloudsat_files:
	cloudsat_data = HDF(cloudsat_granule, HC.READ)
	cs_lats = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Latitude')]
	cs_lons = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Longitude')]
	
	profile_time = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Profile_time')]
	granule_time = cloudsat_granule.split('/')[-1].split('_')[0]
	start_time = datetime.datetime(year = int(granule_time[:4]), month = 1, day = 1, hour = int(granule_time[7:9]), minute = int(granule_time[9:11]))
	start_time += datetime.timedelta(days = int(granule_time[4:7]))
	time = [start_time + datetime.timedelta(seconds = int(a)) for a in profile_time]
	time = np.array(time)
	
	start_chunk = start_time.replace(minute = start_time.minute - start_time.minute%5, second = 0)
	end_chunk = time[-1].replace(minute = time[-1].minute//5 * 5, second = 0)
	num_chunks = int((end_chunk - start_chunk).seconds//300)
	
	five_min_intervals = [start_chunk + datetime.timedelta(minutes = 5 * i) for i in range(num_chunks)]
	#find where cloudsat times ~ 5 minute interval +- 2 seconds
	fmi_indices = [None for a in range(len(five_min_intervals))]
	for n, fmi_t in enumerate(five_min_intervals):
		chunk_index = np.abs(time - fmi_t).argmin()
		if (chunk_index == len(time)) or (chunk_index == 0):
			fmi_indices[n] = chunk_index 
		else:
			fmi_indices[n] = chunk_index - 4
	fmi_indices.append(len(time))
	five_min_intervals.append(end_chunk)
	for n, (start_chunk, end_chunk) in enumerate(zip(fmi_indices[:-1], fmi_indices[1:])):
		HH = five_min_intervals[n].strftime('%H')
		MM = five_min_intervals[n].strftime('%M')
		call_statement = modis_dir.format(year, month, day) + '*.{}{}.*.hdf'.format(HH, MM)
		
		corr_modis_filename = glob.glob(call_statement)
		if len(corr_modis_filename) > 0:
			modis_locs_data = SD(corr_modis_filename[0], SDC.READ)
			modis_latitudes = modis_locs_data.select('Latitude').get()
			modis_longitudes = modis_locs_data.select('Longitude').get()
			print(modis_latitudes)
		sys.exit()
	
	
	











