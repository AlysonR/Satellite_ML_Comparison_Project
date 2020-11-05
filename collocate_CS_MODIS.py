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

def find_scl(temp_list):
	'''
	Parameters:
		temp_list: (list) a temperature list for the cloudsat granule that goes down in height from 0
	Returns:
		scl_i: (int) the height at which any liquid in the cloud would be below freez, or the Super Cooled Level Index
	'''
	
	scl_i = np.abs(temp_list - 263.15).argmin()
	return scl_i

#note this does not take care of the problem of needing leading zeroes on cloudsat diys	
day = '21'
month = '05'
year = 2008

#note, americans would prefer month day year but for the global good i did day month year
print('getting MODIS grids for ', day, month, year)
modis_dir = '/neodc/modis/data/MYD03/collection61/{}/{}/{}/'

diy = datetime.date(year = year, month = int(month), day = int(day)) - datetime.date(year = year, month = 1, day = 1)
diy = diy.days +1
day_before = datetime.date(year = year, month = int(month), day = int(day)) - datetime.timedelta(days = 1)
day_before = (day_before - datetime.date(year = year, month = 1, day = 1)).days + 1

cloudsat_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/cloudsat/2b-geoprof/R05/{}/{}/'
cloudsat_daybefore = sorted(glob.glob(cloudsat_dir.format(year, day_before) + '*.hdf'))[-1]
cloudsat_files = sorted(glob.glob(cloudsat_dir.format(year, diy) + '*.hdf'))
cloudsat_ro_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/cloudsat/2b-cwc-ro/R05/{}/{}/'.format(year, diy)
cloud_type_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/cloudsat/2b-cldclass-lidar/R05/{}/{}/'.format(year, diy)
ecmwf_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/cloudsat/ecmwf-aux/R05/{}/{}/'.format(year, diy)
#note: cloudsat filenames go year, day, HH MM SS at the start

#chunk cloudsat by 5 minutes
cloudsat_chunks = {}
for cloudsat_granule in cloudsat_files:
	cloudsat_data = HDF(cloudsat_granule, HC.READ)
	granule_number = cloudsat_granule.split('/')[-1].split('_')[1]
	
	#super cooled data
	ro_filename = glob.glob(cloudsat_ro_dir + '*_{}_*.hdf'.format(granule_number))[0]
	ro_data = HDF(ro_filename, HC.READ)
	iwp = cloudsat_tools.get_1D_var(ro_data, 'RO_ice_water_path')
	lwp = cloudsat_tools.get_1D_var(ro_data, 'RO_liq_water_path')
	tot_wp = iwp + lwp
	
	ecmwf_filename = glob.glob(ecmwf_dir + '*_{}_*.hdf'.format(granule_number))[0]
	ecmwf_data = SD(ecmwf_filename, SDC.READ)
	temperature = ecmwf_data.select('Temperature').get()
	test = find_scl(temperature[10])
	ecmwf_hdf_data = HDF(ecmwf_filename, HC.READ)
	ec_heights = [a[0] for a in cloudsat_tools.get_1D_var(ecmwf_hdf_data, 'EC_height')]
	sys.exit()
	
	cs_lats = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Latitude')]
	cs_lons = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Longitude')]
	c_indices = list(range(len(cs_lats)))
	
	profile_time = [a[0] for a in cloudsat_tools.get_1D_var(cloudsat_data, 'Profile_time')]
	granule_time = cloudsat_granule.split('/')[-1].split('_')[0]
	start_time = datetime.datetime(year = int(granule_time[:4]), month = 1, day = 1, hour = int(granule_time[7:9]), minute = int(granule_time[9:11]))
	start_time += datetime.timedelta(days = int(granule_time[4:7]))
	time = [start_time + datetime.timedelta(seconds = int(a)) for a in profile_time]
	time = np.array(time)
	
	start_chunk = start_time.replace(minute = start_time.minute - start_time.minute%5, second = 0)
	end_chunk = time[-1].replace(minute = time[-1].minute//5 * 5, second = 0)
	
	num_chunks = int((end_chunk - start_chunk).seconds//300)
	
	five_min_intervals = [start_chunk + datetime.timedelta(minutes = 5 * i) for i in range(num_chunks + 1)]
	#find where cloudsat times ~ 5 minute interval +- 2 seconds
	fmi_indices = [None for a in range(len(five_min_intervals))]
	for n, fmi_t in enumerate(five_min_intervals):
		chunk_index = np.abs(time - fmi_t).argmin()
		fmi_indices[n] = chunk_index 
		
	fmi_indices.append(len(time))
	five_min_intervals.append(end_chunk)
	
	for n, (start_chunk, end_chunk) in enumerate(zip(fmi_indices[:-1], fmi_indices[1:])):
		HH = five_min_intervals[n].strftime('%H')
		MM = five_min_intervals[n].strftime('%M')
		print(time[start_chunk], HH, MM)
		call_statement = modis_dir.format(year, month, day) + '*.{}{}.*.hdf'.format(HH, MM)
		
		corr_modis_filename = glob.glob(call_statement)[0]
		print(corr_modis_filename)
		if len(corr_modis_filename) > 0:
			modis_locs_data = SD(corr_modis_filename, SDC.READ)
			modis_latitudes = modis_locs_data.select('Latitude').get()
			modis_longitudes = modis_locs_data.select('Longitude').get()
			blank_MODIS = [[0 for i in range(len(modis_latitudes[0]))] for j in range(len(modis_latitudes))]
			
			X_row_col = []
			X = []
			
			for i in range(len(modis_latitudes)):
				for j in range(len(modis_latitudes[i])):
					X.append((modis_latitudes[i][j], modis_longitudes[i][j]))
					X_row_col.append((i, j))
			
			X = np.array(X)
			print('Building MODIS Tree')
			modis_KDTree = KDTree(X)
			for c_i, clat, clon in zip(c_indices[start_chunk:end_chunk], cs_lats[start_chunk:end_chunk], cs_lons[start_chunk:end_chunk]):
				d, idx = modis_KDTree.query([(clat, clon)])
				
				mll = X_row_col[idx[0][0]]
				modis_lat = modis_latitudes[mll[0]][mll[1]]
				modis_lon = modis_longitudes[mll[0]][mll[1]]
				#print(modis_lat, modis_lon, clat, clon)
				#print(c_i)
				
				blank_MODIS[mll[0]][mll[1]] = 1.
				
			plt.pcolormesh(modis_latitudes, modis_longitudes, blank_MODIS, cmap = 'inferno')
			plt.show()
			sys.exit()
	
	
	











