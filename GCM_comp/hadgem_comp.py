import numpy as np
import sys
import get_data

hadgem_dir = '/badc/cmip6/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-MM/historical/r1i1p1f3/'


aod550_dir = hadgem_dir + 'Aermon/od550aer/gn/files/d20191207/'
aod870_dir = hadgem_dir + 'Aermon/od870aer/gn/files/d20191207/'
aod440_dir = hadgem_dir + 'Aermon/od440aer/gn/files/d20191207/'

u_dir = hadgem_dir + 'Amon/ua/gn/files/d20191207/'
v_dir = hadgem_dir + 'Amon/va/gn/files/d20191207/'
airt_dir = hadgem_dir + 'Amon/ta/gn/files/d20191207/'
slp_dir = hadgem_dir + 'Amon/psl/gn/files/d20191207/'
rh_dir = hadgem_dir + 'Amon/hur/gn/files/d20191207/'
bl_dir = hadgem_dir + '6hrPlev/bldep/gn/files/d20200923/'
sst_dir = hadgem_dir + 'Omon/tos/gn/files/d20191207/'
spechum_dir = hadgem_dir + 'Amon/hus/gn/files/d20191207/'
omega_dir = hadgem_dir + 'Amon/wap/gn/files/d20191207/'
cf_dir = hadgem_dir + 'Amon/clt/gn/files/d20191207/'
pbl_dir = hadgem_dir + '6hrPlev/bldep/gn/files/d20200923/'
#should compare against calipso to see how ML derived compares to calipso simulator


get_data.get_data(pbl_dir, sst_dir, airt_dir, slp_dir, rh_dir, spechum_dir, omega_dir, u_dir, v_dir, cf_dir)



