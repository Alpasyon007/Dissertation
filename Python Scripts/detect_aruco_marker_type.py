import cv2
import cv2.aruco as aruco
import sys

def detect_aruco_markers(image_path):
	# Load the image
	image = cv2.imread(image_path)

	if image is None:
		print("Image not found.")
		sys.exit(1)

	# Define the ArUco dictionary types to search for
	dictionary_types = [aruco.DICT_4X4_50, aruco.DICT_4X4_100, aruco.DICT_4X4_250,
						aruco.DICT_4X4_1000, aruco.DICT_5X5_50, aruco.DICT_5X5_100,
						aruco.DICT_5X5_250, aruco.DICT_5X5_1000, aruco.DICT_6X6_50,
						aruco.DICT_6X6_100, aruco.DICT_6X6_250, aruco.DICT_6X6_1000,
						aruco.DICT_7X7_50, aruco.DICT_7X7_100, aruco.DICT_7X7_250,
						aruco.DICT_7X7_1000]

	# Detect the ArUco markers using each dictionary type
	for dictionary_type in dictionary_types:
		# Create an ArUco dictionary object of the current type
		dictionary = aruco.getPredefinedDictionary(dictionary_type)

		# Create an ArUco detector object with the current dictionary
		parameters = aruco.DetectorParameters()
		detector = aruco.DetectorParameters()

		# Detect the markers in the image using the current dictionary and detector
		corners, ids, rejected = aruco.detectMarkers(image, dictionary, parameters=parameters)

		# If any markers were found, print the dictionary type and IDs of the detected markers
		if ids is not None:
			print('Dictionary Type: {}'.format(dictionary_type, ids))


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python aruco_detector.py <image_path>")
		sys.exit(1)

	# Get the image path from the command line argument
	image_path = sys.argv[1]

	# Call the function to detect Aruco markers
	detect_aruco_markers(image_path)
