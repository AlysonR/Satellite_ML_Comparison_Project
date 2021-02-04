import numpy as np
import matplotlib.pyplot as plt

vae_ls = np.load('vae_LS.npy')

plt.scatter(vae_ls[:, 0], vae_ls[:, 1])
plt.show()
