import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import grid_from_lat_lon
import map_grid

world_dict = np.load('sgb_no_lwp_96.npy', allow_pickle = True, encoding = 'latin1').item()

X = []
n_bins = 3
omegas = []
eiss = []
rhs = []
ssts = []
binned = [[] for i in range(4)]
values = []
regions = []

for region in sorted(world_dict.keys()):
	xai = world_dict[region]['feature_imp'].tolist()
	#xai.append(np.nanmean(world_dict[region]['values']))
	
	X.append(xai)
	omegas.append(world_dict[region]['feature_imp'][0])
	eiss.append(world_dict[region]['feature_imp'][1])
	rhs.append(world_dict[region]['feature_imp'][2])
	ssts.append(world_dict[region]['feature_imp'][3])
	values.append(np.nanmean(world_dict[region]['values']))
	regions.append(region)

ssts = np.array(ssts)
omegas = np.array(omegas)
eiss = np.array(eiss)
rhs = np.array(rhs)
values = np.array(values)
	
X = np.array(X)

kmeans = KMeans(n_clusters = n_bins, n_init = 5, algorithm = 'full', tol = .000001, max_iter = 60, random_state = 2).fit(X)
labels = np.array(kmeans.labels_)
np.save('labels', [omegas, eiss, rhs, ssts, values, labels])


variable = (labels == 0)
non_variable = np.where(variable == False)[0]
variable = np.where(variable == True)[0]
v_X = X[variable]
#v_X = v_X[:, [0, 2]]

n_clust = 2
v_kms = KMeans(n_clusters = n_clust, n_init = 10, tol = .001, algorithm = 'full', random_state = 2).fit(v_X)
v_labels = v_kms.labels_ + 3

#restructure for variable labels too
newssts = ssts[non_variable].tolist()
newssts.extend(ssts[variable])
neweiss = eiss[non_variable].tolist()
neweiss.extend(eiss[variable])
newlabels = labels[non_variable].tolist()
newlabels.extend(v_labels)
newvalues = values[non_variable].tolist()
newvalues.extend(values[variable])


ssts = newssts
eiss = neweiss
labels = np.array(newlabels)
values = np.array(newvalues)


plt.subplot(121)
plt.scatter(ssts, eiss, c = labels, cmap = plt.cm.get_cmap('tab10', n_bins + n_clust - 1))
plt.ylabel('EIS Importance')
plt.xlabel('SST Importance')
bar = plt.colorbar(ticks = [.4, 1, 1.4, 3], fraction = .2)
bar.ax.set_yticklabels([])
plt.subplot(122)
for b in range((n_clust + n_bins)-1):
	binned[b] = values[np.where((labels == b + 1) == True)[0]]

binned = [np.nanmean(b) for b in binned]

plt.bar(range((n_bins + n_clust)-1), binned)
plt.ylabel('Change in Cloud Fraction from Pristine Environment')
plt.xticks([])
plt.show()

grid, lats, lons = grid_from_lat_lon.make_grid(labels, regions)
map_grid.map_grid(grid, lats, lons, title = 'Regimes from feature importances')



