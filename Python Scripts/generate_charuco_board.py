import cv2
import cv2.aruco as aruco
import numpy as np

# Define the dictionary
dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# Define the Charuco board
charuco_board = aruco.CharucoBoard([8, 8], 0.04, 0.02, dictionary)

image = np.zeros((2000,2000), np.uint8)

# Generate the Charuco board image
charuco_board.generateImage([2000, 2000], image)

# Save the image
cv2.imwrite('charuco_8x8.png', image)