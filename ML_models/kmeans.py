import src
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.svm import SVR



tiles_dir = '/home/users/rosealyd/ML_sat_obs/cloudy_tiles/'
X, y, X_vars = src.get_X_y(tiles_dir, X_vars = ['sst', 'LTS', 'w500', 'RH850', 'RH700'])
for p in range(len(X)):
	X[p].append(y[p])
print(np.array(X).shape)
kmeans = KMeans(n_clusters = 6).fit(X)
labels = kmeans.labels_

plt.scatter([p[-2] for p in X], [p[1] for p in X], c = labels, cmap = 'Set2')
plt.show()
