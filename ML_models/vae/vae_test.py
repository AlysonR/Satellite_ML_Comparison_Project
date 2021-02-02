import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/users/rosealyd/ML_sat_obs/daily/')
import get_day
from sklearn.model_selection import train_test_split



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
#change for global
encoder_inputs = keras.Input(shape = (180, 360, 1))
x = layers.Conv2D(9, 3, activation = 'relu', strides = 2, padding = 'same')(encoder_inputs)
x = layers.Conv2D(18, 3, activation = 'relu', strides = 2, padding = 'same')(x)
x = layers.Flatten()(x)

x = layers.Dense(64, activation = 'relu')(x)
x = layers.Dense(16, activation = 'relu')(x)

z_mean = layers.Dense(latent_dim, name = 'z_mean')(x)
z_log_var = layers.Dense(latent_dim, name = 'z_log_var')(x)
z = Sampling()([z_mean, z_log_var])

encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name = 'encoder')
encoder.summary()


#Decoder
latent_inputs = keras.Input(shape=(latent_dim,))
x = layers.Dense(45 * 90 * 18, activation = 'relu')(latent_inputs)
x = layers.Reshape((45, 90, 18))(x)
x = layers.Conv2DTranspose(18, 3, activation = 'relu', strides = 2, padding = 'same')(x)
x = layers.Conv2DTranspose(9, 3, activation = 'relu', strides = 2, padding = 'same')(x)
decoder_outputs = layers.Conv2DTranspose(1, 3, activation = 'sigmoid', padding = 'same')(x)
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
                    keras.losses.binary_crossentropy(data, reconstruction), axis=(1, 2)
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


data_dict = get_day.get_vars_in_N_grid(['cf'], range(2003, 2017), remove_nans = True)
features = data_dict['cf'][:, :, :, np.newaxis]
print(features.shape)
print(features[:, :, :, 0].ravel().shape)
vae = VAE(encoder, decoder)
vae.compile(optimizer = keras.optimizers.Adam())
vae.fit(features, epochs = 10, batch_size = 1)


def plot_label_clusters(vae, data, labels):
	z_mean, _, _ = vae.encoder.predict(data)
	print(z_mean.shape)
	plt.scatter(z_mean[:, 0], z_mean[:, 1], c = labels)
	plt.colorbar()
	plt.xlabel('z[0]')
	plt.ylabel('z[1]')
	plt.show()

def save_LS(vae, data):
	z_mean, _, _ = vae.encoder.predict(data)
	np.save('vae_LS', z_mean)

save_LS(vae, features)

plot_label_clusters(vae, features[:500, :, :, :], features[:500, :, :, 0].ravel())

	
