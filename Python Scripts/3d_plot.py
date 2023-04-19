import numpy as np

def transform_light_directions(camera_position, camera_transformation, light_directions):

	def normalize(v):
		norm = np.linalg.norm(v)
		if norm == 0:
			return v
		return v / norm

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
		normalized_transformed_light_direction = normalize(transformed_light_direction)

		# Append the transformed light direction to the list
		transformed_light_directions.append(normalized_transformed_light_direction.tolist())

	return transformed_light_directions

def save_directions_to_file(light_directions, filename):
	np.savetxt(filename, light_directions, fmt='%1.8f', delimiter=' ', comments='')

if __name__ == "__main__":
	camera_position = np.array([0.170617, 0.108931, 0.867991])
	camera_transformation = np.array([[ 3.0278144957441955e+03, 0., 8.8458787164804335e+02],
									  [0., 3.4610036988241786e+03, 5.5770685262241136e+02],
									  [0., 0., 1.] ])

	# Load the light directions from the file
	with open("Y:\\Dissertation\\Python Scripts\\directions.txt", "r") as f:
		lines = f.readlines()
		num_lines = len(lines)
		light_directions = np.zeros((num_lines, 3))
		for i in range(num_lines):
			line = lines[i].strip()
			coords = line.split()
			light_directions[i] = [float(coord) for coord in coords]

	transformed_light_directions = transform_light_directions(camera_position, camera_transformation, light_directions)
	save_directions_to_file(transformed_light_directions, "Y:\\Dissertation\\Python Scripts\\light_directions.txt")