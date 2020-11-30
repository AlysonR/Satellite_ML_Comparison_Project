kd = .2854
g = 9.81
Cp = 1005.7
Cv = 719.
Rd = 287.
Rv = 461.
Lv = 2.501 * 10**6
eps = .622

def interp(data, start_lat, start_lon, end_lat, end_lon):
	from scipy import interpolate
	import numpy as np
	function = interpolate.interp2d(start_lon, start_lat, data, kind = 'linear')
	new_data = function(end_lon, end_lat)
	return new_data

def adiabatic_theta(T, p):
	global kd
	#given a Temperature and pressure at some level
	theta = T * ((1000 * 100 / p) ** kd)
	return theta

#given a T700 and T in K and ps in mb
def find_LTS(Ts, T700, ps):
	theta_s = adiabatic_theta(Ts, ps)
	theta_700 = adiabatic_theta(T700, 700. * 100)
	LTS = theta_700 - theta_s

	return LTS
	
#X_vars = ['LTS', 'sst', 'w500', 'RH850', 'tot_ai']
def predict(model_save_name, X, return_model = False):
	import pickle
	trained_model = pickle.load(open(model_save_name, 'rb'))
	if return_model:
		return trained_model
	predicted = trained_model.predict(X)
	return predicted
