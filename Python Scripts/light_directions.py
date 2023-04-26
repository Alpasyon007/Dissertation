import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def calculate_light_directions(radius, num_points):
    angle_step = np.pi / (num_points - 1)
    light_directions = np.zeros((num_points, 3))

    for i in range(0, num_points, 2):
        angle = (3/2) * np.pi + i * angle_step
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        light_directions[i, :] = [y, 0, x]
        light_directions[i + 1, :] = [y, -5, x]

    return light_directions

def transform_to_camera_basis(light_directions, camera_matrix):
    inv_camera_matrix = np.linalg.inv(camera_matrix)
    transformed_light_directions = np.dot(light_directions, inv_camera_matrix.T)
    return transformed_light_directions

def plot_light_directions(light_directions):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for i, direction in enumerate(light_directions):
        ax.scatter(direction[0], direction[1], direction[2])
        ax.text(direction[0], direction[1], direction[2], str(i+1), fontsize=12)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

def save_directions_to_file(light_directions, filename):
    np.savetxt(filename, light_directions, fmt='%1.8f', delimiter=' ', comments='')

# Example usage
radius = 160
num_points = 144
light_directions = calculate_light_directions(radius, num_points)
# transformed_light_directions = transform_to_camera_basis(light_directions, camera_matrix)
plot_light_directions(light_directions)
save_directions_to_file(light_directions, 'directions.txt')