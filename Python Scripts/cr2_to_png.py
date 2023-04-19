from PIL import Image
import os
import sys

# check if the input and output directories are provided as command line arguments
if len(sys.argv) != 3:
	print("Usage: python rename_files.py <input_dir> <output_dir>")
	sys.exit()

# get the input and output directories from the command line arguments
input_dir = sys.argv[1]
output_dir = sys.argv[2]

# get a list of all the files in the input directory
files = os.listdir(input_dir)

# loop through each file in the input directory
for i, filename in enumerate(os.listdir(input_dir)):
	# if filename.endswith(".CR2"):
	# open the CR2 file using PIL
	with Image.open(os.path.join(input_dir, filename)) as im:

		# save the file as a PNG file in the output directory
		im.save(os.path.join(output_dir, str(i) + ".png"))