import glob
import numpy as np
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
import sys
from mpl_toolkits.basemap import Basemap


class MissingFileError(Exception):
	"""Base class for missing a MODIS file"""
	pass

def get_aerosol_props(filename):
	aerosol_dir = '/neodc/modis/data/MOD04_L2/collection61/{}/{}/{}/'
	parts = filename.split('/')
	time = parts[-1].split('.')[2]
	try:
		aerosol_filename = glob.glob(aerosol_dir.format(parts[6], parts[7], parts[8]) + '*.' + time + '.*.hdf')
		print(aerosol_filename)
		aerosol_filename = aerosol_filename[0]
	except IndexError:
		raise MissingFileError
	aerosol_data = SD(aerosol_filename, SDC.READ)
	
	lats = aerosol_data.select('Latitude').get()
	lons = aerosol_data.select('Longitude').get()
	
	eff_rad_attr = aerosol_data.select('Effective_Radius_Ocean').attributes()
	eff_rad = np.array(aerosol_data.select('Effective_Radius_Ocean').get())
	eff_rad_land = eff_rad[0].astype('float')
	eff_rad_ocn = eff_rad[1].astype('float')
	bad_eff = (eff_rad_ocn < 0)
	eff_rad_ocn[bad_eff] = np.nan
	bad_eff = (eff_rad_land < 0)
	eff_rad_land[bad_eff] = np.nan
	eff_rad_ocn = eff_rad_ocn * eff_rad_attr['scale_factor']
	eff_rad_land = eff_rad_land * eff_rad_attr['scale_factor']
	
	aod_attr = aerosol_data.select('AOD_550_Dark_Target_Deep_Blue_Combined').attributes()
	aod = np.array(aerosol_data.select('AOD_550_Dark_Target_Deep_Blue_Combined').get()).astype('float')
	bad_aod = (aod < -100)
	aod[bad_aod] = np.nan
	aod = aod * aod_attr['scale_factor']

	
	ang_attr = aerosol_data.select('Angstrom_Exponent_1_Ocean').attributes()
	ang = aerosol_data.select('Angstrom_Exponent_1_Ocean').get().astype('float')
	bad_ang = (ang < -1000)
	ang = ang * ang_attr['scale_factor']
	ang[bad_ang] = np.nan
	
	ai = aod * ang
	
	return eff_rad_ocn, eff_rad_land, aod, ai, lats, lons
	
def get_tiles(filenames):
	m = Basemap(projection = 'gall', resolution = 'c')
	m.drawcoastlines()
	
	for filename in filenames:
		print(filename)
		try:
			r_ocn, r_land, aods, ais, latitudes, longitudes = get_aerosol_props(filename)
			x,y = m(longitudes, latitudes)
			m.pcolormesh(x, y, ais)
		except MissingFileError:
			print('here')
			#if missing file, can't do full day interpolation and should skip this day
			#raise MissingFile
			pass
	plt.colorbar()
	plt.show()
	sys.exit()
		
			
		

