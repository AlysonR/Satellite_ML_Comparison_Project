import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

world_dict = np.load('sgb_no_lwp_96.npy', allow_pickle = True, encoding = 'latin1').item()

X = []
n_bins = 3
omegas = []
eiss = []
rhs = []
ssts = []
binned = [[] for i in range(n_bins)]
values = []


for region in world_dict.keys():
	xai = world_dict[region]['feature_imp'].tolist()
	#xai.append(np.nanmean(world_dict[region]['values']))
	
	X.append(xai)
	omegas.append(world_dict[region]['feature_imp'][0])
	eiss.append(world_dict[region]['feature_imp'][1])
	rhs.append(world_dict[region]['feature_imp'][2])
	ssts.append(world_dict[region]['feature_imp'][3])
	values.append(np.nanmean(world_dict[region]['values']))
	
X = np.array(X)

kmeans = KMeans(n_clusters = n_bins, n_init = 5, algorithm = 'full', tol = .000001, max_iter = 60, random_state = 1).fit(X)
labels = kmeans.labels_
np.save('labels', [omegas, eiss, rhs, ssts, values, labels])

plt.subplot(121)
plt.scatter(ssts, eiss, c = labels, cmap = plt.cm.get_cmap('tab10', n_bins))
plt.ylabel('EIS Importance')
plt.xlabel('SST Importance')
bar = plt.colorbar(ticks = [.4, 1, 1.4, 3], fraction = .2)
bar.ax.set_yticklabels(['Inversion \n Controlled', 'Variable', 'SST \n Controlled'])

plt.subplot(122)
for label, value in zip(labels, values):
	binned[label].append(value)

binned = [np.nanmean(b) for b in binned]
plt.bar(range(n_bins), binned)
plt.ylabel('Change in Cloud Fraction from Pristine Environment')
plt.show()


