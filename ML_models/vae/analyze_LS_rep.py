import numpy as np
import pickle
import sys
import matplotlib.pyplot as plt
import random
from sklearn.cluster import MiniBatchKMeans, KMeans, SpectralClustering

with open('Bvae_ls_8.pickle', 'rb') as f:
	beta_vae_ls = pickle.load(f)
	
ctype = 'spectral'

zmean = beta_vae_ls[0]
cf = np.array(beta_vae_ls[1])

sample = random.sample(range(zmean.shape[0]), 1000)

n_clust = 9
if ctype == 'kmeans':
	cluster = KMeans(n_clusters = n_clust).fit(zmean)
	
labels = np.array(cluster.labels_)
plt.scatter(zmean[:, 1][sample], cf[sample], c = labels[sample])
plt.show()
