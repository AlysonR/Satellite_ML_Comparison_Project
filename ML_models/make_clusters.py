import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
import grid_from_lat_lon
import matplotlib.pyplot as plt
import pickle
import matplotlib.cm as cm
from sklearn.metrics import explained_variance_score
import cmap

res = 2
with open('imp_dic_{}.txt'.format(res), 'rb') as f:
	importances_dict = pickle.load(f)

#X_vars = ['EIS', 'sst', 'RH700', 'tot_aod','tot_ang', 'upper_level_winds', 'w500', 'evap']

#number regimes (1x1, 13; 4x4, 7)

importances = []
fits = []
areas = []
lons = []
for key in importances_dict.keys():
	importances.append(importances_dict[key]['imps'])
	#importances.append([p for i, p in enumerate(importances_dict[key]['imps']) if i not in [4]])
	fits.append(importances_dict[key]['r2'])
	areas.append(key)
	lons.append(float(key.split('_')[1]))

importances = np.array(importances)
print(importances.shape)
fits_grid, lats, lons = grid_from_lat_lon.make_grid(fits, areas, res = res)
plt.pcolormesh(lons, lats, fits_grid)
plt.colorbar()
plt.show()


'''
temps = []
for n in range(3, 15):
	clustering = KMeans(n_clusters = n, max_iter = 1000, tol = 1e-7)
	clustering.fit(importances)
	temps.append(float(clustering.inertia_))
plt.scatter(range(3, 15), temps)
plt.show()
sys.exit()
'''


print(importances.shape)
print('fitting')
n = 13
#clustering = AgglomerativeClustering(n_clusters = n, compute_full_tree = True)
#clustering = KMeans(n_clusters = n, max_iter = 1000, verbose = 10, tol = 1e-7)
clustering = SpectralClustering(n_clusters = n, degree = 3, n_init = 30, assign_labels = 'discretize')
clustering.fit(importances)
labels = clustering.labels_

with open('sc_{}_{}.pickle'.format(res, n), 'wb') as f:
	pickle.dump([labels, areas, importances], f)
#np.save('evap_kmeans_{}'.format(n), [labels, areas, importances])

first_dim = [i[0] for i in importances]
second_dim = [i[2] for i in importances]
plt.scatter(first_dim[::10], second_dim[::10], c = labels[::10])
plt.show()

qmap = cm.get_cmap('plasma', n + 1)
grid, lats, lons = grid_from_lat_lon.make_grid(labels, areas, res = res)
plt.pcolormesh(lons, lats, grid, cmap = qmap)
cbar = plt.colorbar(ticks = np.linspace(.5, 12.5, 14))
cbar.ax.set_yticklabels(['{}'.format(p) for p in range(0, 14)])
plt.show()



