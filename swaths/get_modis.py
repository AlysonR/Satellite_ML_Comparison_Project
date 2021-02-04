import numpy as np
import glob
from pyhdf.SD import SD, SDC
import sys
import matplotlib.pyplot as plt
import tools
from scipy import interpolate

modis_dir = '/neodc/modis/data/MYD06_L2/collection61/{}/{}/{}/'
dump_dir = '/gws/nopw/j04/aopp/douglas/modis_tiles/'

def interp_through_nan(data):
	x = np.arange(0, data.shape[1])
	y = np.arange(0, data.shape[0])
	data = np.ma.masked_invalid(data)
	xx, yy = np.meshgrid(x, y)
	x1 = xx[~data.mask]
	y1 = yy[~data.mask]
	newdata = data[~data.mask]
	
	gd = interpolate.griddata((x1, y1), newdata.ravel(), (xx, yy), method = 'cubic')
	return gd

def get_lat_lons(year, month, day, time):
	lat_lon_dir = '/neodc/modis/data/MYD03/collection61/{}/{}/{}/'.format(year, month, day)
	onedeg_data = SD(glob.glob(lat_lon_dir + '*.{}.*.hdf'.format(time))[0], SDC.READ)
	latitude = onedeg_data.select('Latitude').get().astype(float)
	longitude = onedeg_data.select('Longitude').get().astype(float)
	return latitude, longitude

def bits_stripping(bit_start,bit_count,value):
	bitmask=pow(2,bit_start+bit_count)-1
	return np.right_shift(np.bitwise_and(value,bitmask),bit_start)

def get_modis(year, month, day):
	global modis_dir
	root_dir = modis_dir.format(year, month, day)
	
	for filename in sorted(glob.glob(root_dir + '*.hdf'))[15:19]:
		identifier = filename.split('/')[-1][:-4]
		
		temp_modis_data = SD(filename, SDC.READ)
		time = filename.split(root_dir)[-1].split('.')[2]
		#for var in temp_modis_data.datasets():
		#	print(var)
		latitudes, longitudes = get_lat_lons(year, month, day, time)
		lwp = temp_modis_data.select('Cloud_Water_Path_1621').get().astype(float) 
		
		bad = (lwp < 0)
		lwp[bad] = np.nan
		if np.count_nonzero(np.isnan(lwp)) > 0:
			print('interpolating the bad')
			test_lwp = interp_through_nan(lwp)
			plt.subplot(121)
			plt.pcolormesh(lwp)
			plt.subplot(122)
			plt.pcolormesh(test_lwp)
			plt.show()
		
		
		re_attrs = temp_modis_data.select('Cloud_Effective_Radius').attributes()
		re = temp_modis_data.select('Cloud_Effective_Radius').get().astype(float) * re_attrs['scale_factor']
		bad = (re < 0)
		re[bad] = np.nan
		
		cth = temp_modis_data.select('cloud_top_height_1km').get().astype(float)
		bad = (cth < 0)
		cth[bad] = np.nan
		
		cloud_mask = temp_modis_data.select('Cloud_Mask_1km').get()
		test_mask = bits_stripping(1, 2, cloud_mask[:, :, 0])
		test_mask = np.array(test_mask).astype(float)
		bad = (test_mask < 0)
		test_mask[bad] = np.nan
		ratio_bad = np.count_nonzero(np.isnan(test_mask))/(1030.*1354.)
		print(ratio_bad)
		print(np.count_nonzero(np.isnan(test_mask)))
		
		if ratio_bad < .01:
			print('good enough ratio')
			swath_dict = {}
			swath_dict['cloud'] = test_mask
			swath_dict['lwp'] = lwp
			swath_dict['re'] = re
			swath_dict['cth'] = cth
		
		
			temp = []
			for key in swath_dict.keys():
				variable = swath_dict[key]
				variable = variable[15:1015, 2:1052]
				print(variable.shape)
				test_blocks = tools.blockshaped(variable, 50, 50)
				temp.append(test_blocks)
			temp = np.array(temp)
			temp = np.rollaxis(temp, 0, 4)
			latitudes = tools.blockshaped(latitudes[15:-15, 2:-2], 50, 50)
			longitudes = tools.blockshaped(longitudes[15:-15, 2:-2], 50, 50)
			#np.save({'lats': latitudes, 'lons': longitudes, 'X': temp}, dump_dir + identifier)
		
