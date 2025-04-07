import tkinter as tk
from tkinter import filedialog
from config import Config
from process import process_gcode

def main():
    # Create root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open file dialog for selecting .gcode file
    gcode_file = filedialog.askopenfilename(
        title="Select GCode File",
        filetypes=[("GCode Files", "*.gcode"), ("All Files", "*.*")]
    )

    if gcode_file:
        try:
            # Load machine config
            config = Config.from_file('machine.toml')

            # Read gcode file
            with open(gcode_file, 'r') as f:
                input_gcode = f.read()

            # Process the gcode
            output = process_gcode(input_gcode, config)
            
            # Write output to file
            output_file = gcode_file.rsplit('.', 1)[0] + '_processed.gcode'
            with open(output_file, 'w') as f:
                f.write(output['gcode'])

            print(f"Processing complete. Output written to: {output_file}")

            # check the config object for statistics
            if 'statistics' in output:
                print("\nStatistics:")
                print("-" * 50)
                for key, value in output['statistics'].items():
                    print(f"{key:<25} {float(value):.5g}" if isinstance(value, (int, float)) else f"{key:<25} {value}")
                print("-" * 50)

        except Exception as e:
            print(f"Error processing file: {str(e)}")
    else:
        print("No file selected")

if __name__ == "__main__":
    main()
