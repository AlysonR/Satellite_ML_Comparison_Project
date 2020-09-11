import glob
import numpy as np
from pyhdf.SD import SD, SDC
import sys
import matplotlib.pyplot as plt

def convert_to_byte(byte_value):
	return str(format(abs(byte_value), '08b'))

test_filename = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd06_l2/2007/213/MYD06_L2.A2007213.0125.061.2018042223349.hdf'

level_data = SD(test_filename, SDC.READ)
re = level_data.select('Cloud_Effective_Radius').get()
lwp = level_data.select('Cloud_Water_Path').get()/1000.
cth = level_data.select('Cloud_Top_Height').get()

ctt = level_data.select('Cloud_Top_Temperature').get() - level_data.select('Cloud_Top_Temperature').attributes()['add_offset'] 
ctt = ctt * level_data.select('Cloud_Top_Temperature').attributes()['scale_factor']
print(np.amin(ctt), np.amax(ctt))
latitutdes = level_data.select('Latitude').get()
longitudes = level_data.select('Longitude').get()

plt.subplot(121)
plt.pcolormesh(lwp)
plt.colorbar()
print(ctt)
print (np.amin(ctt), np.amax(ctt))
plt.subplot(122)
plt.pcolormesh(ctt, vmin = 150, vmax = 350)
plt.colorbar()
plt.show()
sys.exit()





