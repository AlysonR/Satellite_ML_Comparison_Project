import numpy as np
from sklearn.cluster import AgglomerativeClustering
import grid_from_lat_lon
import matplotlib.pyplot as plt
import pickle

with open('imp_dic.txt', 'rb') as f:
	importances_dict = pickle.load(f)

#X_vars = ['EIS', 'sst', 'RH700', 'tot_aod','tot_ang', 'upper_level_winds', 'w500']

importances = []
fits = []
areas = []
for key in importances_dict.keys():
	importances.append(importances_dict[key]['imps'])
	fits.append(importances_dict[key]['r2'])
	areas.append(key)
importances = np.array(importances)
print(importances.shape)
print('fitting')
clustering = AgglomerativeClustering(n_clusters = 8)
clustering.fit(importances)
print(clustering.n_clusters)
labels = clustering.labels_
print(labels.shape)
first_dim = [i[0] for i in importances]
second_dim = [i[1] for i in importances]
plt.scatter(first_dim, second_dim, c = labels)
plt.show()


grid, lats, lons = grid_from_lat_lon.make_grid(labels, areas)
plt.pcolormesh(lons, lats, grid)
plt.colorbar()
plt.show()



