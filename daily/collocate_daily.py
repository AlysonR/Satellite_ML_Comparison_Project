import numpy as np
import get_daily_MODIS
import datetime
import get_merra
import get_SST

year = '2007'
month = '01'
day = '20'

monthly_dict = {'cwp': [], 'iwp': [], 'cth': [], 'cod': [], 'l_re': [], 'i_re': [], 'cf': [], 'modis_aod': [], 
'EIS': [], 'LTS': [], 'w500': [], 'u500': [], 'v500': [], 'u850': [], 'v850': [], 'u700': [], 'v700': [], 'usfc': [], 
'vsfc': [], 'RH900': [], 'RH850': [], 'RH700': [], 'evap': [], 'sens_h': [], 'latent_h': [], 'su_ai': [], 'su_aod': [],
'du_ai': [], 'du_aod': [], 'oc_ai': [], 'oc_aod': [], 'bc_ai': [], 'bc_aod': [], 'ss_ai': [], 'ss_aod': [], 
'tot_ai': [], 'tot_aod': [], 'tot_ang': [], 'sst': []}
merra_keys = ['EIS', 'LTS', 'w500', 'u500', 'v500', 'u850', 'v850', 'u700', 'v700', 'usfc', 'vsfc', 'RH900', 'RH850', 'RH700', 'evap', 'sens_h', 'latent_h','su_ai', 'su_aod', 'du_ai', 'du_aod', 'oc_ai', 'oc_aod', 'bc_ai', 'bc_aod', 'ss_ai', 'ss_aod', 'tot_ai', 'tot_ang', 'tot_aod']
monthrange = range(1, 31)
for n in monthrange:
	day = datetime.date(year = int(year), month = int(month), day = n).strftime('%d')
	mo_lats, mo_lons, modis_dict = get_daily_MODIS.get_day(year, month, day)
	for key in modis_dict.keys():
		monthly_dict[key].append(modis_dict[key])
	merra_dict = get_merra.get_daily(year, month, day, mo_lats, mo_lons)
	for key in merra_keys:
		monthly_dict[key].append(merra_dict[key])
	monthly_dict['sst'].append(get_SST.find_sst(year, month, day, mo_lats, mo_lons))
	monthly_dict['lats'] = mo_lats
	monthly_dict['lons'] = mo_lons

np.save('{}_{}_test'.format(month, year), monthly_dict)
	
