import glob
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

def preprocess_image_for_model(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img28 = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
    img28 = img28.astype("float32") / 255.0
    img_reshaped = img28.reshape(1, 28, 28, 1)
    return img_reshaped

def main():
    results = [0,0,0,0,0,0,0,0,0,0]
    images = glob.glob('./digits/*')
    model = load_model('./mnist_cnn.h5')
    for img_path in images:
        img = preprocess_image_for_model(img_path)
        prediction = model.predict(img)
        digit = np.argmax(prediction)
        results[digit] += 1
    print(results)
    print(sum(results))

main()