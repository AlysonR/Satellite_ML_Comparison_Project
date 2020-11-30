import numpy as np
kd = .2854
g = 9.81
Cp = 1005.7
Cv = 719.
Rd = 287.
Rv = 461.
Lv = 2.501 * 10**6
eps = .622

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
	
#Given a T in K and an RH in %
#Returns Td in K
def find_Td(T, RH):
	Td = T - (100 - RH)/5.
	return Td

def find_LCL(T, RH):
	Td = find_Td(T, RH)
	LCL = 125 * (T - Td)
	return LCL

def find_rh(Qv, p, T):
	e = (Qv * p) / (.622 + (.378 * Qv))
	es = find_es(T)
	rh = e/es
	return rh

def find_es(T):
	T -= 273.15
	B = 1730.63
	A = 8.07131
	C = 233.426
	es = 10. ** (A - (B/(C + T)))
	#convert to pa
	es *= 133.32
	return es
	
def find_km(wvmr):
	#wvmr is the wter vapor mixing ratio
	kmoist = .2854 * (1 - .24 * wmvr)
	return kmoist

def find_Qs(T, p):
	es = find_es(T)
	Qs = 621.97 * (es / (p - es))
	#convert to kg/kg from g/kg
	Qs /= 1000.
	return Qs
	
def find_gamma_v(T, p):
	global g, Cp, Lv, Rv, Rd
	Qs = find_Qs(T, p)
	gamma_v = (g/Cp) * ((1 + ((Lv * Qs)/(Rd * T))) / (1 + ((Lv**2) * Qs)/(Cp * Rv * T**2)))
	return gamma_v

def find_gamma_m(T, p):
	global g, Cp
	gamma_d = g / Cp
	gamma_v = find_gamma_v(T, p)
	gamma_m = gamma_d - gamma_v
	return gamma_m


def interp(data, start_lat, start_lon, end_lat, end_lon):
	from scipy import interpolate
	
	function = interpolate.interp2d(start_lon, start_lat, data, kind = 'linear')
	new_data = function(end_lon, end_lat)
	return new_data
	

def find_EIS(Ts, T700, ps, RHs, Z700, T_prof, heights, pres_prof, pbl_z):
	zLCL = find_LCL(Ts, RHs)
	i_LCL = np.abs(heights - zLCL).argmin()
	
	TLCL = T_prof[i_LCL]
	pLCL = pres_prof[i_LCL]
	
	LTS = find_LTS(Ts, T700, ps)
	gamma_700 = find_gamma_m(T700, 700 * 100.)
	gamma_LCL = find_gamma_m(TLCL, pLCL)
	EIS = LTS - (gamma_700 * (Z700-pbl_z)) + (gamma_LCL * (pbl_z - zLCL))
	return EIS
