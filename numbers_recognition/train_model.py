import tensorflow as tf
from tensorflow.keras import datasets, layers, models

def train_model_cnn():
    (x_train, y_train), (x_test, y_test) = datasets.mnist.load_data()

    x_train = x_train.astype('float32') / 255.0
    x_test  = x_test.astype('float32') / 255.0

    x_train = x_train[..., None]
    x_test = x_test[..., None]

    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation = 'relu', input_shape=(28,28,1)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(10, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    model.fit(x_train, y_train, epochs=5)
    model.save('mnist_cnn.h5')

train_model_cnn()
