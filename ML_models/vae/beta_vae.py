import numpy as np
import tensorflow as tf
from tensorflow import keras
print("Num GPUs available", len(tf.config.experimental.list_physical_devices('GPU')))
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import pickle
import sys
sys.path.append('/home/users/rosealyd/ML_sat_obs/daily/')
import get_day
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import random
import sample_layer

feature_names = ['sst', 'EIS', 'RH700', 'w500', 'tot_aod', 'tot_ang', 'u850', 'evap']
feature_names = ['EIS', 'RH700']
res = 4
batch_s = 64
n_epochs = 20
vae_gamma = 10
vae_capacity = 25
class Sampling(layers.Layer):
	'''Uses (z_mean, z_log_var) to sasmple z, the vector ecoding the cloud feature'''
	
	def call(self, inputs):
		z_mean, z_log_var = inputs
		batch = tf.shape(z_mean)[0]
		dim = tf.shape(z_mean)[1]
		epsilon = tf.keras.backend.random_normal(shape = (batch, dim))
		return z_mean + tf.exp(.5 * z_log_var) * epsilon
		
	
#Encoder
latent_dim = 2

encoder_inputs = keras.Input(shape = (res, res, len(feature_names)))
x = layers.Conv2D(16, 4, activation = 'relu', strides = 2, padding = 'same')(encoder_inputs)
x = layers.Conv2D(32, 4, activation = 'relu', strides = 2, padding = 'same')(x)

x = layers.Flatten()(x)
x = layers.BatchNormalization()(x)
x = layers.Activation('relu')(x)
x = layers.Dense(units = 256)(x)
x = layers.BatchNormalization()(x)
x = layers.Activation('relu')(x)
x = layers.Dense(units = latent_dim * 2, activation = 'relu')(x)

z_mean = layers.Dense(latent_dim, activation = 'linear', name = 'z_mean')(x)
z_log_var = layers.Dense(latent_dim, activation = 'linear', name = 'z_log_var')(x)
z = sample_layer.SampleLayer(vae_gamma, vae_capacity,'beta_sampling_layer')([z_mean, z_log_var])

encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name = 'encoder')
encoder.summary()

#Decoder
latent_inputs = keras.Input(shape=(latent_dim,))
x = layers.Dense(units = 256)(latent_inputs)
x = layers.BatchNormalization()(x)
x = layers.Activation('relu')(x)
x = layers.Dense(units = 256)(x)
x = layers.BatchNormalization()(x)
x = layers.Activation('relu')(x)

#x = layers.Dense(units = 512, activation = 'relu')(x)
#x = layers.BatchNormalization()(x)
x = layers.Reshape((-1, 1, 256), input_shape = (256,))(x)

x = layers.Conv2DTranspose(32, 4, strides = 1, padding = 'same')(x)
x = layers.Conv2DTranspose(16, 4, strides = 2, padding = 'same')(x)

decoder_outputs = layers.Conv2DTranspose(len(feature_names), 4, strides = 2, padding = 'same', activation = 'tanh')(x)
decoder = keras.Model(latent_inputs, decoder_outputs, name = 'decoder')
decoder.summary()

class VAE(keras.Model):
    def __init__(self, encoder, decoder, **kwargs):
        super(VAE, self).__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.total_loss_tracker = keras.metrics.Mean(name="total_loss")
        self.reconstruction_loss_tracker = keras.metrics.Mean(
            name="reconstruction_loss"
        )
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")

    @property
    def metrics(self):
        return [
            self.total_loss_tracker,
            self.reconstruction_loss_tracker,
            self.kl_loss_tracker,
        ]

    def train_step(self, data):
        with tf.GradientTape() as tape:
            z_mean, z_log_var, z = self.encoder(data)
            reconstruction = self.decoder(z)
            reconstruction_loss = tf.reduce_mean(
                tf.reduce_sum(
                    keras.losses.mean_squared_error(data, reconstruction), axis=(1, 2)
                )
            )
            kl_loss = -0.5 * (1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
            kl_loss = tf.reduce_mean(tf.reduce_sum(kl_loss, axis=1))
            total_loss = reconstruction_loss + kl_loss
        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        self.total_loss_tracker.update_state(total_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        return {
            "loss": self.total_loss_tracker.result(),
            "reconstruction_loss": self.reconstruction_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
        }


#data_dict = get_day.get_vars_in_N_grid(['cf'], range(2003, 2017), remove_nans = True)
data_dict = get_day.get_large_X_y(feature_names, 'cf', range(2003, 2020), fill_value = -100, nr = res, nc = res)
features = data_dict['X']

for dimension in range(features.shape[-1]):
	minimum_value = np.nanmin(features[:, :, :, dimension]) * -1
	maximum_value = np.nanmax(features[:, :, :, dimension])
	test = features[:, :, :, dimension] + minimum_value
	test = test / (minimum_value + maximum_value)
	test[np.isnan(test)] = -1
	features[:, :, :, dimension] = test
data_dict['X'] = features
 
assert not np.any(np.isnan(features)), 'nans still in data'
print(np.count_nonzero(np.isnan(features)), 'make doubly triply quadruply spit on it sure there are no nans')
print(np.nanmin(features), np.nanmax(features))
vae = VAE(encoder, decoder)
vae.compile(optimizer = keras.optimizers.Adam())
history = vae.fit(features, epochs = n_epochs, batch_size = batch_s)

def plot_loss(history):
	a = plt.plot(range(n_epochs), history.history['kl_loss'], c = 'r', label = 'kl')
	plt.twinx()
	b = plt.plot(range(n_epochs), history.history['reconstruction_loss'], c = 'b', label = 'reconstruction')
	plt.savefig('loss_Bvae')
	plt.clf()

#np.save('vae_trained', vae)

def plot_label_clusters(vae, data, labels):
	print(data.shape, labels.shape)
	print(np.nanmin(data), np.nanmax(data))
	z_mean, _, _ = vae.encoder.predict(data)
	print(z_mean.shape)
	plt.scatter(z_mean[:, 0], z_mean[:, 1], c = labels, vmin = 0, vmax = 1)
	plt.colorbar()
	plt.xlabel('z[0]')
	plt.ylabel('z[1]')
	plt.savefig('Bvae_LS')
	#plt.show()
def save_LS(vae, data):
	z_mean, _, _ = vae.encoder.predict(data)
	with open('Bvae_ls_{}_{}.pickle'.format(latent_dim, n_epochs), 'wb') as f:
		pickle.dump([z_mean, np.nanmean(data_dict['y'], axis = (1, 2))], f)
	#with open('Bvae_model_{}_{}.pickle'.format(latent_dim, n_epochs), 'wb') as f:
		#pickle.dump(vae, f)

save_LS(vae, features)

sample = random.sample(range(features.shape[0]), 1000)

plot_loss(history)

plot_label_clusters(vae, data_dict['X'][sample], np.nanmean(data_dict['y'][sample], axis = (1, 2)))

	
