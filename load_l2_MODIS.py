import glob
import numpy as np
from pyhdf.SD import SD, SDC
import sys

def convert_to_byte(byte_value):
	print(byte_value)
	return format(byte_value[0], '08b')

test_filename = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c6/myd06_l2/2007/213/MYD06_L2.A2007213.2110.006.2014053183031.hdf'

level_data = SD(test_filename, SDC.READ)
re = level_data.select('Cloud_Effective_Radius').get()
lwp = level_data.select('Cloud_Water_Path').get()
cth = level_data.select('Cloud_Top_Height').get()
ctt = level_data.select('Cloud_Top_Temperature').get()
latitutdes = level_data.select('Latitude').get()
longitudes = level_data.select('Longitude').get()

#first byte is if its determined, 0 not, 1 determined
#to determine cloud fraction, use the 2nd byte of the cloud mask
#0 is cloudy, 1 is probably cloudy, 2 is probably clear, 3 is clear
#include 0 and 1 in cloud_fraction
#have just 0 as certain_cloud_fraction
cloud_mask = level_data.select('Cloud_Mask_1km').get()
print(cloud_mask[0][0][0], cloud_mask.shape)
print(format(cloud_mask[0][0][0], '08b'))
byte_converter = np.vectorize(convert_to_byte)
test = byte_converter(cloud_mask)
print(test[0][0])
sys.exit()





