import numpy as np
import glob
import datetime
import get_modis_monthly
import matplotlib.pyplot as plt

year = '2007'
day = '01'
month = '01'
diy = datetime.date(year = int(year), month = int(month), day = int(day)).strftime('%j')
print(diy)
aqua_modis_monthly_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd08_m3/{}/{}/'.format(year, diy)


for filename in glob.glob(aqua_modis_monthly_dir + '*.hdf'):
	print(filename)
	latitudes, longitudes, lwp, iwp, cth, cod, l_re, i_re, cloudfrac, aod = get_modis_monthly.get_data(filename)

	plt.pcolormesh(longitudes, latitudes, cloudfrac)
