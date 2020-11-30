import glob
import datetime
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt
import sys
import numpy as np

modis_daily_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/mod08_d3/'

def get_day(year, month, day):
	date = datetime.date(year = int(year), month = int(month), day = int(day))
	diy = date.strftime('%j')
	filename = glob.glob(modis_daily_dir + '*A{}{}*.hdf'.format(year, diy))[0]
	print(filename)
	
	modis_data = SD(filename, SDC.READ)
	
	modis_latitudes = modis_data.select('YDim').get()
	modis_longitudes = modis_data.select('XDim').get()
	
	cwp = modis_data.select('Cloud_Water_Path_Liquid_Mean').get().astype(float)
	bad = (cwp < -1)
	cwp[bad] = np.nan
	iwp = modis_data.select('Cloud_Water_Path_Ice_Mean').get().astype(float)
	bad = (iwp < -1)
	iwp[bad] = np.nan
	
	cth = modis_data.select('Cloud_Top_Height_Mean').get().astype(float)
	bad = (cth < -1)
	cth[bad] = np.nan
	#change to km
	cth = cth/1000.
	#in the future may want to look at diurnal variation
	#cth_day = modis_data.select('Cloud_Top_Height_Day_Mean').get()
	#cth_night = modis_data.select('Cloud_Top_Height_Night_Mean').get()
	
	cod_attrs = modis_data.select('Cloud_Optical_Thickness_Combined_Mean').attributes()
	cod = modis_data.select('Cloud_Optical_Thickness_Combined_Mean').get().astype(float) * cod_attrs['scale_factor']
	bad = (cod < -1)
	cod[bad] = np.nan
	
	l_attrs = modis_data.select('Cloud_Effective_Radius_Liquid_Mean').attributes()
	l_re = modis_data.select('Cloud_Effective_Radius_Liquid_Mean').get().astype(float) * l_attrs['scale_factor']
	bad = (l_re < -1)
	l_re[bad] = np.nan
	
	#microns
	i_attrs = modis_data.select('Cloud_Effective_Radius_Ice_Mean').attributes()
	i_re = modis_data.select('Cloud_Effective_Radius_Ice_Mean').get().astype(float) * i_attrs['scale_factor']
	bad = (i_re < -1)
	i_re[bad] = np.nan
	
	cf_attrs = modis_data.select('Cloud_Fraction_Mean').attributes()
	cf = modis_data.select('Cloud_Fraction_Mean').get().astype(float) * cf_attrs['scale_factor']
	bad = (cf < 0)
	cf[bad] = np.nan
	
	aod_attrs = modis_data.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean').attributes()
	aod = modis_data.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean').get().astype(float) * aod_attrs['scale_factor']
	bad = (aod < 0)
	aod[bad] = np.nan
	
	modis_dict = {'cwp': cwp, 'iwp': iwp, 'cth': cth, 'cod': cod, 'l_re': l_re, 'i_re': i_re, 'cf': cf, 'modis_aod': aod}
	
	return modis_latitudes, modis_longitudes, modis_dict
