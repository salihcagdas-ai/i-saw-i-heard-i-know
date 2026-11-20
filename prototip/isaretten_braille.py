# Import necessary libraries
import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# Define a simple dataset of signs and their corresponding Braille representation
signs = {'A': '⠈⠈', 'B': '⠃⠃', 'C': '⠉⠉'}
braille_labels = {'⠈⠈': 'A', '⠃⠃': 'B', '⠉⠉': 'C'}

# Function to preprocess the input sign image
def preprocess_image(image_path):
    try:
        # Read the image from the file
        image = cv2.imread(image_path)

        # Resize the image to a fixed size (e.g., 64x64 pixels)
        image = cv2.resize(image, (64, 64))

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Flatten the image into a 1D array
        features = gray_image.flatten()

        # Normalize the features to a consistent scale
        features = features / 255.0  # Assuming pixel values are in the range [0, 255]

        return features

    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

# Function to recognize the sign using a simple K-nearest neighbors classifier
def recognize_sign(features):
    X_train = np.array(list(signs.values()))
    y_train = list(signs.keys())
    knn = KNeighborsClassifier(n_neighbors=1)
    knn.fit(X_train, y_train)

    # Predict the label for the input features
    prediction = knn.predict([features])
    return prediction[0]

# Function to translate the recognized sign to Braille
def translate_to_braille(sign):
    return braille_labels.get(sign, 'Unknown')

# Main function to perform the translation
def sign_to_braille_translation(image_path):
    # Preprocess the input image
    features = preprocess_image(image_path)

    if features is not None:
        # Recognize the sign
        sign = recognize_sign(features)

        # Translate the recognized sign to Braille
        braille_translation = translate_to_braille(sign)

        return braille_translation
    else:
        return "Error in image preprocessing"

# Example usage
image_path = 'path/to/your/sign_image.jpg'
result = sign_to_braille_translation(image_path)
print(f"Braille Translation: {result}")
