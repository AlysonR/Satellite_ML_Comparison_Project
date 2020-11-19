import numpy as np
import glob
import datetime
import get_modis_monthly
import matplotlib.pyplot as plt
import get_merra
import get_seawifs
import sys
import get_sst

year = '2004'
year_dict = {}
variables = ['latitudes', 'longitudes', 'sst', 'lwp', 'iwp', 'cth', 'cod', 'l_re', 'i_re', 'cf', 'modis_aod']
aerosol_vars = ['bc_ang', 'bc_aod', 'bc_ai', 'du_ang', 'du_aod', 'du_ai', 'oc_ang', 'oc_aod', 'oc_ai', 'su_ang', 'su_aod', 'su_ai', 'ss_ang', 'ss_aod', 'ss_ai', 'tot_ang', 'tot_aod', 'tot_ai', 'w500', 'LTS', 'upper_level_U', 'upper_level_V', 'upper_level_winds', 'U_850', 'V_850', 'U_500', 'V_500', 'RH850', 'RH700']

for varname in variables:
	year_dict[varname] = []
for varname in aerosol_vars:
	year_dict[varname] = []

aqua_modis_monthly_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd08_m3/{}/'.format(year)


for filename in sorted(glob.glob(aqua_modis_monthly_dir + '*/*.hdf')):
	try:
		print(filename)
		diy = filename.split('/')[-1].split('.')[1].split(year)[-1]
		date = datetime.date(year = int(year), month = 1, day = 1) + datetime.timedelta(days = int(diy) - 1)
		month = date.strftime('%m')
		print(month)
		#print('getting seawifs')
		#sat_aero = get_seawifs.get_aerosol(year, month)
		
		print('getting MODIS')
		latitudes, longitudes, lwp, iwp, cth, cod, l_re, i_re, cloudfrac, aod = get_modis_monthly.get_data(filename)
		
		year_dict['latitudes'] = latitudes
		year_dict['longitudes'] = longitudes	
		year_dict['lwp'].append(lwp)
		year_dict['iwp'].append(iwp)
		year_dict['cth'].append(cth)
		year_dict['cod'].append(cod)
		year_dict['l_re'].append(l_re)
		year_dict['i_re'].append(i_re)
		year_dict['cf'].append(cloudfrac)
		year_dict['modis_aod'].append(aod)
		
		print('getting sst')
		ssts = get_sst.get_sst_avhrr(year, month, latitudes, longitudes)
		year_dict['sst'].append(ssts)
		
		
		print('getting MERRA')
		merra_vars = get_merra.get_file(year, month, latitudes, longitudes)
		for var in merra_vars.keys():
			year_dict[var].append(merra_vars[var])
	except IndexError:
		print('Skipping missing MERRA')	
np.save(year, year_dict)
	
	
