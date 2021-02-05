import matplotlib.pyplot as plt
import numpy as np
import cmap



array = [[.9855, .9851, .9827, 1.0], [.9995, .9990, 1.0, np.nan], [.9994, 1.0, np.nan, np.nan], [1.0, np.nan, np.nan, np.nan]]

plt.pcolormesh(array, cmap = 'plasma', vmin = .985, vmax = 1.)
plt.xticks([.5, 1.5, 2.5, 3.5], ['RF', 'SGB', 'XGBoost', 'MVLR'], size = 16)
plt.yticks([3.5, 2.5, 1.5, .5], ['RF', 'SGB', 'XGBoost', 'MVLR'], size = 16)
plt.subplots_adjust(left = .2)
cbar = plt.colorbar()
cbar.set_label('Similarity Score', size = 16)
cbar.ax.tick_params(size = 15)
plt.show()
