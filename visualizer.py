import tkinter as tk
from tkinter import filedialog
import re

import numpy as np
import matplotlib.pyplot as plt

from config import Config
from util import list_of_int_to_list_of_bits

def extract_layer_data(p):
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select GCode file",
        filetypes=[("GCode files", "*.gcode"), ("All files", "*.*")]
    )
    
    if not file_path:
        print("No file selected. Exiting.")
        return
    
    # Ask for layer number
    try:
        layer_number = int(input("Enter the layer number to extract: "))
        if layer_number < 0:
            print("Layer number must be positive. Exiting.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number. Exiting.")
        return
    
    # Define patterns to match
    layer_start_pattern = f";Layer{layer_number}"
    next_layer_pattern = f";Layer{layer_number + 1}"
    valve_pattern = r"VALVES_SET VALUES=([\d\.\s,]+)"
    g1_pattern = r"G1 Y([\d\.]+)"
    return_pattern = r"SET_SECOND_PASS"
    
    # Initialize variables
    in_target_layer = False
    extracted_data = []
    current_y = None
    
    try:
        with open(file_path, 'r') as file:
            going_up = True
            for line in file:
                # Check if we've entered the target layer
                if layer_start_pattern in line:
                    in_target_layer = True
                    continue
                
                # Check if we've reached the next layer
                if next_layer_pattern in line:
                    in_target_layer = False
                    break
                
                # Only process lines if we're in the target layer
                if in_target_layer:
                    # Check for G1 X command
                    g1_match = re.search(g1_pattern, line)
                    if g1_match:
                        current_y = float(g1_match.group(1))
                    
                    return_match = re.search(return_pattern, line)
                    if return_match:
                        going_up = False

                    # Check for valve values in the line
                    valve_match = re.search(valve_pattern, line)
                    if valve_match and current_y is not None:
                        valve_values = valve_match.group(1).strip()
                        # Split by comma and convert to list of numbers
                        values = [np.uint8(v) for v in valve_values.split(',')]
                        v = np.array(values, dtype=np.uint8)
                        b = list_of_int_to_list_of_bits(v)

                        #b_expanded = np.zeros(len(b)*2, dtype=np.uint8)
                        try:
                            if going_up:
                                p[::2,int(current_y)] = b
                            else:
                                p[1::2,int(current_y)+1] = b
                        
                        except IndexError as e:
                            print(f"IndexError: {e}")


                        #if len(values) == 11:  # Ensure we have 11 values
                        #    extracted_data.append({
                        #        'y_position': current_y,
                        #        'valve_values': values
                        #    })
    
        # Display results
        if not p:
            print(f"No data found for layer {layer_number}.")
        else:
            return p
                
    except FileNotFoundError:
        print(f"Could not open file: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def plot_binary_array(binary_array):
    """
    Plot a 2D numpy array of 1's and 0's as a monochrome image.
    
    Parameters:
        binary_array (numpy.ndarray): A 2D array containing only 1's and 0's
    """
    # Verify the input is a 2D array
    if binary_array.ndim != 2:
        raise ValueError("Input must be a 2D numpy array")
    
    # Create a new figure and axis
    plt.figure(figsize=(6, 6))
    
    # Plot the array as an image
    # - cmap='binary' uses white for 0 and black for 1
    # - interpolation='nearest' ensures no smoothing between pixels
    plt.imshow(binary_array, cmap='binary', interpolation='nearest')
    
    # Remove axis ticks for cleaner visualization
    plt.xticks([])
    plt.yticks([])
    
    # Add a tight layout and display the plot
    plt.tight_layout()
    plt.show()


def main():
    config = Config.from_file('machine.toml')
    
    p = np.zeros(config.get_bed_array_size(), dtype=np.uint8)
    extract_layer_data(p)
    
    plot_binary_array(p[:,1::2])

    input("press enter to close")

if __name__ == "__main__":
    main()