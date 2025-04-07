import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def visualize_3d_coordinates(coordinates):
    """
    Visualize a list of 3D coordinates with unique numbers at each point
    
    Parameters:
    coordinates (list): List of (x, y, z) tuples or lists
    """
    # Convert input to numpy array for easier handling
    coords = np.array(coordinates)
    
    # Create the 3D figure
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot each point
    ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], color='red', s=100, alpha=0.7)
    
    # Add number labels at each point
    for i, (x, y, z) in enumerate(coords):
        ax.text(x, y, z, str(i+1), color='black', fontsize=12, fontweight='bold',
                ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Set axis labels
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    
    # Set a title
    ax.set_title('3D Visualization of Coordinates')
    
    # Adjust view angle
    ax.view_init(elev=30, azim=45)
    
    # Add a grid
    ax.grid(True)
    
    # Adjust the axes limits to provide some padding
    x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
    y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
    z_min, z_max = coords[:, 2].min(), coords[:, 2].max()
    
    # Add some padding around the points
    padding = max(
        (x_max - x_min) * 0.1,
        (y_max - y_min) * 0.1,
        (z_max - z_min) * 0.1,
        1.0  # Minimum padding
    )
    
    ax.set_xlim(x_min - padding, x_max + padding)
    ax.set_ylim(y_min - padding, y_max + padding)
    ax.set_zlim(z_min - padding, z_max + padding)
    
    # Show the plot
    plt.tight_layout()
    plt.show()

# Example usage with sample coordinates
if __name__ == "__main__":
    # Sample list of 10 3D coordinates
    sample_coordinates = [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (2, 5, 8),
        (9, 6, 3),
        (5, 1, 7),
        (3, 8, 2),
        (6, 3, 9),
        (8, 4, 1),
        (5, 7, 5)
    ]
    
    # Visualize the coordinates
    visualize_3d_coordinates(sample_coordinates)