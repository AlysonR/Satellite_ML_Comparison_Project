import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
import grid_from_lat_lon
import matplotlib.pyplot as plt
import pickle
import matplotlib.cm as cm
from sklearn.metrics import explained_variance_score

with open('imp_dic_evaptest.txt', 'rb') as f:
	importances_dict = pickle.load(f)

#X_vars = ['EIS', 'sst', 'RH700', 'tot_aod','tot_ang', 'upper_level_winds', 'w500']

importances = []
fits = []
areas = []
for key in importances_dict.keys():
	importances.append(importances_dict[key]['imps'])
	#importances.append([p for i, p in enumerate(importances_dict[key]['imps']) if i not in [4]])
	fits.append(importances_dict[key]['r2'])
	areas.append(key)
importances = np.array(importances)

'''
temps = []
for n in range(6, 26, 3):
	clustering = KMeans(n_clusters = n, max_iter = 1000, verbose = 10, tol = 1e-7)
	clustering.fit(importances)
	temps.append(float(clustering.inertia_))
plt.scatter(range(6, 26, 3), temps)
plt.show()
sys.exit()'''
	

print(importances.shape)
print('fitting')
n = 13
#clustering = AgglomerativeClustering(n_clusters = n, compute_full_tree = True)
#clustering = KMeans(n_clusters = n, max_iter = 1000, verbose = 10, tol = 1e-7)
clustering = SpectralClustering(n_clusters = n, n_init = 30, assign_labels = 'discretize')
clustering.fit(importances)
labels = clustering.labels_

np.save('evap_kmeans_{}'.format(n), [labels, areas])

first_dim = [i[-1] for i in importances]
second_dim = [i[1] for i in importances]
plt.scatter(first_dim[::10], second_dim[::10], c = labels[::10])
plt.show()

qmap = cm.get_cmap('plasma', n)
grid, lats, lons = grid_from_lat_lon.make_grid(labels, areas)
plt.pcolormesh(lons, lats, grid, cmap = qmap)
plt.colorbar()
plt.show()



