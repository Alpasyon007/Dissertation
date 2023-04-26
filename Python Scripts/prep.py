import os
import rawpy
from PIL import Image, ImageTk
import logging
import argparse
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import imghdr

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create the Tk object
root = tk.Tk()
root.withdraw()

parser = argparse.ArgumentParser(description='Resize image files')
parser.add_argument('directory', nargs='?', help='Path to the directory containing the image files')
parser.add_argument('output_directory', nargs='?', help='Path to the output directory')
parser.add_argument('--resize', action='store_true', help='If images should be resized')
parser.add_argument('--no-resize', dest='resize', action='store_false', help='If images should be resized')
parser.add_argument('--width', type=int, default=1456, help='Width of the resized images (default: 1456)')
parser.add_argument('--height', type=int, default=976, help='Height of the resized images (default: 976)')
parser.add_argument('--crop', action='store_true', help='If images should be cropped')
parser.add_argument('--no-crop', dest='crop', action='store_false', help='If images should be cropped')
parser.set_defaults(crop=True)
parser.set_defaults(resize=True)
args = parser.parse_args()

directory = args.directory
output_directory = args.output_directory
size = (args.width, args.height)
names_file = 'names.txt'

if not args.directory or not args.output_directory:
	parser.print_usage()
else:
	if args.resize:
		# Create the output directory if it doesn't exist
		if not os.path.exists(output_directory):
			logging.info(f'Creating output directory: {output_directory}')
			os.makedirs(output_directory)

		for filename in os.listdir(directory):
			if filename.endswith('.CR2'):  # modify extensions as needed
				logging.info(f'Resizing {filename}...')
				with rawpy.imread(os.path.join(directory, filename)) as raw:
					rgb = raw.postprocess()
					im = Image.fromarray(rgb)

					# Resize the image
					im_resized = im.resize(size)

					output_path = os.path.join(output_directory, filename)
					im_resized.save(output_path, format='PNG')  # specify the output format as JPEG
				logging.info(f'Saved {filename} as {os.path.basename(output_path)}')
			if filename.endswith('.png'):  # modify extensions as needed
				logging.info(f'Resizing {filename}...')
				with Image.open(os.path.join(directory, filename)) as im:
					# Resize the image
					im_resized = im.resize(size)

					output_path = os.path.join(output_directory, filename)
					im_resized.save(output_path, format='PNG')  # specify the output format as PNG
				logging.info(f'Saved {filename} as {os.path.basename(output_path)}')
		logging.info(f'Done Resizing!')

	if args.crop:
		logging.info(f'Starting Cropping')
		# Select an image for cropping using a file dialog
		file_path = filedialog.askopenfilename(initialdir=output_directory, title='Select an image for cropping')

		if file_path:
			logging.info(f'Opening image for crop area selection')
			# Load the image for cropping
			im = Image.open(file_path)

			# Create a new window for displaying the image
			top = tk.Toplevel()
			top.title('Select Crop Region')

			# Create a canvas for displaying the image
			canvas = tk.Canvas(top, width=im.width, height=im.height)
			canvas.pack()

			# Convert the image to a Tkinter PhotoImage for display
			im_tk = ImageTk.PhotoImage(im)
			canvas.create_image(0, 0, anchor='nw', image=im_tk)

			# Define variables to store the selection rectangle
			selection_rect = None
			selection_rect_start = None

			# Define a function for handling mouse button presses
			def on_button_press(event):
				global selection_rect, selection_rect_start
				selection_rect_start = (event.x, event.y)
				if selection_rect:
					canvas.delete(selection_rect)
				selection_rect = canvas.create_rectangle(0, 0, 0, 0, outline='red')

			# Define a function for handling mouse motion while the button is pressed
			def on_button_motion(event, im):
				global selection_rect
				if selection_rect:
					canvas.delete(selection_rect)
					x0, y0 = selection_rect_start
					x1, y1 = (event.x, event.y)
					x0, y0, x1, y1 = tuple(int(coord / im_tk.width() * im.width) for coord in (x0, y0, x1, y1))
					if x0 > x1:
						x0, x1 = x1, x0
					if y0 > y1:
						y0, y1 = y1, y0
					width = x1 - x0
					height = y1 - y0
					if width > height:
						y1 = y0 + width
					else:
						x1 = x0 + height
					selection_rect = canvas.create_rectangle(x0, y0, x1, y1, outline='red')

			# Define a function for handling mouse button releases
			def on_button_release(event, im):
				global selection_rect, selection_rect_start, top
				if selection_rect:
					canvas.delete(selection_rect)
					selection_rect = None
				x0, y0 = selection_rect_start
				x1, y1 = (event.x, event.y)
				x0, y0, x1, y1 = tuple(int(coord / im_tk.width() * im.width) for coord in (x0, y0, x1, y1))
				if x0 > x1:
					x0, x1 = x1, x0
				if y0 > y1:
					y0, y1 = y1, y0
				width = x1 - x0
				height = y1 - y0
				if width > height:
					y1 = y0 + width
				else:
					x1 = x0 + height

				# Convert the crop coordinates to the original image size
				x0, y0, x1, y1 = tuple(int(coord / im_tk.width() * im.width) for coord in (x0, y0, x1, y1))

				# Crop and save each image in the output directory
				for filename in os.listdir(output_directory):
					if filename.endswith('.CR2'):
						logging.info(f'Cropping {filename}...')
						with Image.open(os.path.join(output_directory, filename)) as im:
							# Crop the image
							im_cropped = im.crop((x0, y0, x1, y1))

							output_path = os.path.join(output_directory, filename)
							im_cropped.save(output_path, format='PNG')
					if filename.endswith('.png'):
						logging.info(f'Cropping {filename}...')
						with Image.open(os.path.join(output_directory, filename)) as im:
							# Crop the image
							im_cropped = im.crop((x0, y0, x1, y1))

							output_path = os.path.join(output_directory, filename)
							im_cropped.save(output_path, format='PNG')

				logging.info(f'Done Cropping!')
				top.destroy()

			# Bind the canvas to mouse button presses and releases
			canvas.bind('<ButtonPress-1>', on_button_press)
			canvas.bind('<B1-Motion>', lambda event: on_button_motion(event, im))
			canvas.bind('<ButtonRelease-1>', lambda event: on_button_release(event, im))

			top.wait_window(canvas)

	file_list = os.listdir(output_directory)
	output_file = open(os.path.join(output_directory, names_file), 'w')
	logging.info(f'Creating {names_file} file')

	for file_name in file_list:
		output_file.write(file_name + '\n')
	logging.info(f'Finished!')