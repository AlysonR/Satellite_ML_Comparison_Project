import numpy as np
import subprocess
import sys
import h5py
import matplotlib.pyplot as plt

def get_aerosol(year, month):
	wifs_dict = {}

	url_name = 'https://measures.gesdisc.eosdis.nasa.gov/data/DeepBlueSeaWiFS_Level3/SWDB_L3M10.004/{}/DeepBlue-SeaWiFS-1.0_L3M_{}{}_v004-20130604T132056Z.h5'.format(year, year, month)
	call_string= 'curl -n -c ~/.urs_cookies -b ~/.urs_cookies -LJO --url {}'
	subprocess.call(call_string.format(url_name).split())
	
	aerosol_filename = 'DeepBlue-SeaWiFS-1.0_L3M_{}{}_v004-20130604T132056Z.h5'.format(year, month)
	
	aerosol_data = h5py.File(aerosol_filename, 'r')
	
	wifs_dict['aod'] = aerosol_data['aerosol_optical_thickness_550_land_ocean'][:]
	wifs_dict['ang'] = aerosol_data['angstrom_exponent_land_ocean'][:]
	bad = ((wifs_dict['aod'] == -999.) | (wifs_dict['ang'] == -999))
	wifs_dict['ai'] = wifs_dict['aod'] * wifs_dict['ang']
	wifs_dict['ai'][bad] = np.nan
	wifs_dict['aod'][bad] = np.nan
	wifs_dict['ang'][bad] = np.nan
	
	latitudes = aerosol_data['latitude'][:]
	longitudes = aerosol_data['longitude'][:]
	
	remove_string = 'rm {}'.format(aerosol_filename)
	subprocess.call(remove_string.split())
	
	return wifs_dict
