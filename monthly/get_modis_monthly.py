import numpy as np
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt

def get_data(filename):
	dataset = SD(filename, SDC.READ)
	lats = dataset.select('YDim').get()
	lons = dataset.select('XDim').get()
	
	cwp = dataset.select('Cloud_Water_Path_Liquid_Mean_Mean').get() * dataset.select('Cloud_Water_Path_Liquid_Mean_Mean').attributes()['scale_factor']
	bad = (cwp < -1)
	cwp[bad] = np.nan
	
	iwp = dataset.select('Cloud_Water_Path_Ice_Mean_Mean').get() * dataset.select('Cloud_Water_Path_Ice_Mean_Mean').attributes()['scale_factor']
	bad = (iwp < -1)
	iwp[bad] = np.nan
	
	cth = dataset.select('Cloud_Top_Height_Mean_Mean').get() * dataset.select('Cloud_Top_Height_Mean_Mean').attributes()['scale_factor']
	bad = (cth < -1)
	cth[bad] = np.nan
	
	cod = dataset.select('Cloud_Optical_Thickness_Combined_Mean_Mean').get() * dataset.select('Cloud_Optical_Thickness_Combined_Mean_Mean').attributes()['scale_factor']
	bad = (cod < -5)
	cod[bad] = np.nan
	
	
	lre = dataset.select('Cloud_Effective_Radius_Liquid_Mean_Mean').get() * dataset.select('Cloud_Effective_Radius_Liquid_Mean_Mean').attributes()['scale_factor']
	bad = (lre < -1)
	lre[bad] = np.nan
	
	ire = dataset.select('Cloud_Effective_Radius_Ice_Mean_Mean').get() * dataset.select('Cloud_Effective_Radius_Ice_Mean_Mean').attributes()['scale_factor']
	bad = (ire < -1)
	ire[bad] = np.nan
	
	cf =  dataset.select('Cloud_Fraction_Mean_Mean').get() * dataset.select('Cloud_Fraction_Mean_Mean').attributes()['scale_factor']
	bad = (cf < -1)
	cf[bad] = np.nan
	
	aod = dataset.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean').get() * dataset.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean').attributes()['scale_factor']
	bad = (aod < -1)
	aod[bad] = np.nan
	
	return lats, lons, cwp, iwp, cth, cod, lre, ire, cf, aod
