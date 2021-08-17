import tensorflow as tf
import matplotlib.pyplot as plt


# import digit dataset
mnist = tf.keras.datasets.mnist
(tx, ty), (vx, vy) = mnist.load_data()

# preprocess input types
tx = tx[:,:,:,None].astype('float32')
vx = vx[:,:,:,None].astype('float32')
ty = ty.astype(int)
vy = vy.astype(int)

# display relevant info
print("""tx:%s, ty:%s
vx:%s, vy:%s""" % (tx.shape, ty.shape, vx.shape, vy.shape))

# create a grid of plots
f, axs = plt.subplots(10,10,figsize=(10,10))

# plot a sample number into each subplot
for i in range(10):
  for j in range(10):
    # get a sample image for the 'i' number
    img = tx[ty==i,:,:,0][j,:,:]

    # plot image in axes
    axs[i,j].imshow(img, cmap='gray')

    # remove x and y axis
    axs[i,j].axis('off')

# remove unecessary white space
plt.tight_layout()

# display image
plt.show()

# defines a standard 2d convolution block with batch normalisation, 
# relu activation, max pooling and dropout

def normConvBlock(filters, return_model=True, name=None):
  lays = [
    tf.keras.layers.Conv2D(filters, 3, padding='valid', name=name+'_conv'),
    tf.keras.layers.BatchNormalization(name=name+'_bn'),
    tf.keras.layers.Activation('relu', name=name+'_act'),
    tf.keras.layers.MaxPooling2D(2, strides=2, name=name+'_mpool'),
    tf.keras.layers.Dropout(0.1, name=name+'_drop'),
  ]

  if return_model:
    return tf.keras.models.Sequential(lays, name=name)
  else:
    return lays
	
# create NN model
model = tf.keras.models.Sequential()
model.add(normConvBlock(64, name='b1'))
model.add(normConvBlock(128, name='b2'))
model.add(tf.keras.layers.Flatten(name='flat'))
model.add(tf.keras.layers.Dense(10, activation='softmax', name='logit'))

# compile model with adam optimizer and crossentropy loss
# note that 'sparse_categorical_crossentropy' loss should be used as our target
# is encoded as ordinal. if using one hot change this to 'categorical_crossentropy'
model.compile('adam', 'sparse_categorical_crossentropy', metrics=['acc'])

# test model with a sample image
_ = model(tx[:1,:,:,:])

# summary of model structure
tf.keras.utils.plot_model(
    model, 
    show_shapes=True, 
    show_layer_names=True, 
    show_dtype=True,
    expand_nested=True,
    dpi = 50
)

# define an early stopping callback. This callback will load the iteration with
# the best val loss at the end of training
es_call = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', min_delta=0, patience=2, verbose=0,
    mode='auto', baseline=None, restore_best_weights=True
)

# fit the model with the mnist dataset
history = model.fit(tx, ty, validation_data=(vx, vy), epochs=20, batch_size=1024, callbacks=[es_call])

