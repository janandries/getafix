import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as colors

def visualize_3d_matrix_optimized(matrix, point_coordinates=None, alpha=0.7):
    """
    Visualize a 3D matrix where 1s represent the presence of objects - optimized version
    
    Parameters:
    matrix (numpy.ndarray): 3D numpy array where 1s represent object presence
    point_coordinates (list, optional): List of (x, y, z) coordinates to overlay with numbers
    alpha (float): Transparency of the voxels (0.0 to 1.0)
    """
    # Create figure and 3D axis
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Get the coordinates of the filled voxels
    filled_voxels = np.where(matrix == 1)
    
    # Set colormap
    cmap = plt.cm.viridis
    
    # Use voxels function for batch rendering instead of individual cubes
    # Create a 3D matrix of the same shape as input but filled with color values
    colors_matrix = np.zeros(matrix.shape + (4,))  # RGBA
    colors_matrix[filled_voxels] = cmap(0.7)
    
    # Set alpha
    colors_matrix[..., 3] = alpha * matrix
    
    # Create a boolean matrix for voxel visibility
    voxels = matrix.astype(bool)
    
    # Plot all voxels at once (much faster)
    ax.voxels(voxels, facecolors=colors_matrix, edgecolor='k', linewidth=0.3)
    
    # Add numbered points if provided
    if point_coordinates is not None:
        coords = np.array(point_coordinates)
        # Plot each point
        ax.scatter(coords[:, 0], coords[:, 1], coords[:, 2], 
                   color='red', s=100, alpha=1.0, edgecolors='black')
        
        # Add number labels at each point
        for i, (x, y, z) in enumerate(coords):
            ax.text(x, y, z, str(i+1), color='white', fontsize=12, fontweight='bold',
                    ha='center', va='center', bbox=dict(facecolor='black', alpha=0.7, edgecolor='none'))
    
    # Set axis labels
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    
    # Set title
    ax.set_title('3D Matrix Visualization (Optimized)')
    
    # Set axis limits
    ax.set_xlim(-0.5, matrix.shape[0] - 0.5)
    ax.set_ylim(-0.5, matrix.shape[1] - 0.5)
    ax.set_zlim(-0.5, matrix.shape[2] - 0.5)
    
    # Add a grid
    ax.grid(True)
    
    # Adjust view angle
    ax.view_init(elev=30, azim=45)
    
    plt.tight_layout()
    plt.show()

def create_sphere_in_matrix(matrix_shape, center, radius):
    """
    Create a sphere represented by 1s in a 3D matrix - optimized version
    
    Parameters:
    matrix_shape (tuple): Shape of the 3D matrix (x, y, z)
    center (tuple): Center coordinates of the sphere (x, y, z)
    radius (float): Radius of the sphere
    
    Returns:
    numpy.ndarray: 3D matrix with 1s representing the sphere
    """
    # Create coordinate grids (this approach is faster for large matrices)
    x = np.arange(matrix_shape[0])
    y = np.arange(matrix_shape[1])
    z = np.arange(matrix_shape[2])
    
    # Create meshgrid
    x, y, z = np.meshgrid(x, y, z, indexing='ij')
    
    # Calculate distance from each point to the center (vectorized)
    distance = np.sqrt(
        (x - center[0])**2 + 
        (y - center[1])**2 + 
        (z - center[2])**2
    )
    
    # Create the sphere matrix
    return (distance <= radius).astype(int)

def create_cube_in_matrix(matrix_shape, start, size):
    """
    Create a cube represented by 1s in a 3D matrix
    
    Parameters:
    matrix_shape (tuple): Shape of the 3D matrix (x, y, z)
    start (tuple): Starting coordinates of the cube (x, y, z)
    size (int): Size of the cube
    
    Returns:
    numpy.ndarray: 3D matrix with 1s representing the cube
    """
    # Create an empty matrix
    matrix = np.zeros(matrix_shape, dtype=int)
    
    # Calculate end coordinates with bounds checking
    end_x = min(start[0] + size, matrix_shape[0])
    end_y = min(start[1] + size, matrix_shape[1])
    end_z = min(start[2] + size, matrix_shape[2])
    
    # Set the cube region to 1 (using direct slice assignment - very fast)
    matrix[start[0]:end_x, start[1]:end_y, start[2]:end_z] = 1
    
    return matrix

def create_pyramid_in_matrix(matrix_shape, base_center, height):
    """
    Create a pyramid represented by 1s in a 3D matrix - optimized version
    
    Parameters:
    matrix_shape (tuple): Shape of the 3D matrix (x, y, z)
    base_center (tuple): Center coordinates of the pyramid base (x, y, z)
    height (int): Height of the pyramid
    
    Returns:
    numpy.ndarray: 3D matrix with 1s representing the pyramid
    """
    # Pre-allocate the matrix (faster than incremental building)
    matrix = np.zeros(matrix_shape, dtype=int)
    
    # Calculate base dimensions
    base_size = height * 2 - 1
    base_start_x = max(0, base_center[0] - height + 1)
    base_start_y = max(0, base_center[1] - height + 1)
    
    # Build the pyramid in a more vectorized way
    for h in range(height):
        layer_size = base_size - (h * 2)
        if layer_size <= 0:
            break
            
        layer_start_x = base_start_x + h
        layer_start_y = base_start_y + h
        z_level = base_center[2] + h
        
        # Make sure we're within bounds
        if z_level >= matrix_shape[2]:
            break
            
        # Set the layer using a single assignment
        end_x = min(layer_start_x + layer_size, matrix_shape[0])
        end_y = min(layer_start_y + layer_size, matrix_shape[1])
        
        if layer_start_x < end_x and layer_start_y < end_y:
            matrix[layer_start_x:end_x, layer_start_y:end_y, z_level] = 1
    
    return matrix

def combine_matrices(*matrices):
    """
    Combine multiple 3D matrices using logical OR - optimized
    
    Parameters:
    *matrices: Variable number of 3D numpy arrays
    
    Returns:
    numpy.ndarray: Combined 3D matrix
    """
    if not matrices:
        return None
    
    # Use logical_or.reduce for efficiency with multiple matrices
    return np.logical_or.reduce(matrices).astype(int)

# Example usage with smaller matrix size for speed
if __name__ == "__main__":
    # Use smaller matrix for faster rendering
    matrix_shape = (15, 15, 15)
    
    # Create a sphere
    sphere_matrix = create_sphere_in_matrix(
        matrix_shape=matrix_shape,
        center=(5, 5, 5),
        radius=3
    )
    
    # Create a cube
    cube_matrix = create_cube_in_matrix(
        matrix_shape=matrix_shape,
        start=(9, 9, 2),
        size=4
    )
    
    # Create a pyramid
    pyramid_matrix = create_pyramid_in_matrix(
        matrix_shape=matrix_shape,
        base_center=(7, 3, 9),
        height=4
    )
    
    # Combine all shapes
    combined_matrix = combine_matrices(sphere_matrix, cube_matrix, pyramid_matrix)
    
    # Define some interesting coordinates to label
    point_coordinates = [
        (5, 5, 5),     # Center of sphere
        (11, 11, 4),   # Inside cube
        (7, 3, 12),    # Top of pyramid
        (2, 10, 8),    # Empty space
        (7, 7, 7)      # Random point
    ]
    
    # Visualize the combined matrix with the optimized function
    visualize_3d_matrix_optimized(combined_matrix, point_coordinates)