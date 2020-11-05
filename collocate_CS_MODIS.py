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


def find_closest_h(h_list, point):
	'''
	Parameters:
		point: (int/float) the point (a height) that you are trying to find the other closest point in the list to
		h_list: (list) the list that you are trying to find the closest items to the point to
	Returns:
		h_i: (int) the index of the closest item in the list to the point
	'''
	h_i = np.abs(h_list - point).argmin()
	return h_i
def get_sc(list_of_temps, ecmwf_heights, cloudsat_heights, liq_wc):
	sc_ls = []
	for i in range(len(list_of_temps)):
		ec_h = ecmwf_heights[find_closest_h(list_of_temps[i], 263.15)]
		cs_i = find_closest_h(cloudsat_heights[i], ec_h) + 1
		sc_liq = liq_wc[i][:cs_i]
		temp = cloudsat_heights[i][:cs_i]
		lwp = 0
		for wc, ztop, zbot in zip(sc_liq, temp[:-1], temp[1:]):
			dz = ztop - zbot
			if wc > 0:
				lwp += dz * wc
		sc_ls.append(lwp)
	
	return sc_ls	
	
#note this does not take care of the problem of needing leading zeroes on cloudsat diys	
day = '21'
month = '05'
year = 2008

#note, americans would prefer month day year but for the global good i did day month year
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
	ro_data = SD(ro_filename, SDC.READ)
	lwc = ro_data.select('RO_liq_water_content').get()
	heights = ro_data.select('Height').get()
	ro_hdf_data = HDF(ro_filename, HC.READ)
	lwp = np.array([a[0] for a in cloudsat_tools.get_1D_var(ro_hdf_data, 'RO_liq_water_path')])
	iwp = np.array([a[0] for a in cloudsat_tools.get_1D_var(ro_hdf_data, 'RO_ice_water_path')])
	tot_path = lwp + iwp
	
	ecmwf_filename = glob.glob(ecmwf_dir + '*_{}_*.hdf'.format(granule_number))[0]
	ecmwf_data = SD(ecmwf_filename, SDC.READ)
	temperature = ecmwf_data.select('Temperature').get()
	
	ecmwf_hdf_data = HDF(ecmwf_filename, HC.READ)
	ec_heights = [a[0] for a in cloudsat_tools.get_1D_var(ecmwf_hdf_data, 'EC_height')]
	sc_levels = np.array(get_sc(temperature, ec_heights, heights, lwc))/1000.
	#using the supercooled liquid water path from sc_levels, divid by total water path to get supercoold liq frac
	slf = sc_levels / tot_path
	
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
			ds = []
			for c_i, clat, clon in zip(c_indices[start_chunk:end_chunk], cs_lats[start_chunk:end_chunk], cs_lons[start_chunk:end_chunk]):
				d, idx = modis_KDTree.query([(clat, clon)])
				ds.append(d[0])
				mll = X_row_col[idx[0][0]]
				modis_lat = modis_latitudes[mll[0]][mll[1]]
				modis_lon = modis_longitudes[mll[0]][mll[1]]
				#print(modis_lat, modis_lon, clat, clon)
				#print(c_i)
				
				blank_MODIS[mll[0]][mll[1]] = 1.0
				
			plt.plot(ds)
	plt.show()
	sys.exit()
	
	
	











