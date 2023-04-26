import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def transform_light_directions(camera_position, camera_transformation, light_directions):

	# def normalize(v):
	# 	norm = np.linalg.norm(v)
	# 	if norm == 0:
	# 		return v
	# 	return v / norm

	# Transform light directions
	transformed_light_directions = []
	for light_direction in light_directions:
		# Convert to numpy array
		light_direction = np.array(light_direction)

		# Subtract camera position to translate to camera coordinates
		translated_light_direction = light_direction - camera_position

		# Apply camera transformation
		transformed_light_direction = camera_transformation.dot(translated_light_direction)

		# Normalize the transformed light direction
		# normalized_transformed_light_direction = normalize(transformed_light_direction)

		# Append the transformed light direction to the list
		transformed_light_directions.append(transformed_light_direction)

	return np.array(transformed_light_directions)

def save_directions_to_file(light_directions, filename):
	np.savetxt(filename, light_directions, fmt='%1.8f', delimiter=' ', comments='')


def read_light_directions(file_path):
	directions = []

	with open(file_path, 'r') as file:
		for line in file.readlines():
			x, y, z = map(float, line.strip().split())
			directions.append([x, y, z])

	return np.array(directions)

def plot_light_directions(directions):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	xs, ys, zs = directions[:, 0], directions[:, 1], directions[:, 2]
	ax.scatter(xs, ys, zs)

	ax.set_xlabel('X')
	ax.set_ylabel('Y')
	ax.set_zlabel('Z')

	plt.show()

def main():
	camera_position = np.array([0.170617, 0.108931, 0.867991])
	camera_transformation = np.array([[ 3.0278144957441955e+03, 0., 8.8458787164804335e+02],
									  [0., 3.4610036988241786e+03, 5.5770685262241136e+02],
									  [0., 0., 1.] ])
	file_path = 'directions.txt'
	light_directions = read_light_directions(file_path)
	transformed_light_directions = transform_light_directions(camera_position, camera_transformation, light_directions)
	plot_light_directions(transformed_light_directions)
	save_directions_to_file(transformed_light_directions, "transformed_light_directions.txt")

if __name__ == "__main__":
	main()