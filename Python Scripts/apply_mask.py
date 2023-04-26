import os
import cv2
import sys

# check if the input and output directories are provided as command line arguments
if len(sys.argv) != 2:
	print("Usage: python rename_files.py <input_dir>")
	sys.exit()

# get the input directory from the command line arguments
dir_path = sys.argv[1]

# Load the mask
mask_path = os.path.join(dir_path, 'mask.png')
mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

# Iterate over all files in the directory
for filename in os.listdir(dir_path):
	# Check if the file is an image
	if filename.endswith('.png'):
		# Load the image
		img_path = os.path.join(dir_path, filename)
		img = cv2.imread(img_path)

		# Apply the mask
		img = cv2.bitwise_and(img, img, mask=mask)

		# Save the masked image
		masked_path = os.path.join(dir_path, 'masked_' + filename)
		cv2.imwrite(masked_path, img)