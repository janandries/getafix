import logging
from gcode import GCodeMove
import math
from pattern import Pattern
import re
import numpy as np
from util import list_of_bits_to_list_of_int
from config import Config

logger = logging.getLogger(__name__)

def print_begin_cmd(number_of_layers: int) -> str:
    return (
        f"SET_PRINT_STATS_INFO TOTAL_LAYER={number_of_layers}\n"
        "G90\n"
        "G28 X Y\n"
        "SET_FIRST_PASS\n"
        "RESET_Z_PLATFORM\n"
        "G4 P1500  ; wait for servo\n"
        "VALVES_SET VALUES=0,0,0,0,0,0,0,0,0,0,0\n"
        "VALVES_ENABLE ; change to VALVES_DISABLE to do run without valves active\n\n"
    )

def print_end_cmd(number_of_layers: int) -> str:
    return f"; total layers count = {number_of_layers}\n"

def layer_begin_cmd(layer_idx: int, x_maximum_position: int, deposition_rate: int) -> str:
    return (
        f";Layer{layer_idx+1}\n"
        f"SET_PRINT_STATS_INFO CURRENT_LAYER={layer_idx+1}\n"
        f"RESPOND MSG=\"Start layer {layer_idx+1}\"\n"
        "FILL_HOPPER_ASYNC\n"
        "SET_FIRST_PASS\n"
        "Z_ONE_LAYER\n"
        "WAIT_FOR_MACHINE_READY\n"
        f"G1 X{x_maximum_position} F{deposition_rate}; deposit material\n"
    )

def layer_return_cmd(y_return_position: int, y_feed_rate: int) -> str:
    """Generate the GCode commands for returning the print head to a specified Y position.

    This command sequence moves the print head to the end y position, disables all valves,
    moves slightly past that position to make sure the valves are closed
    prepares for the second pass

    Args:
        y_return_position (int): The Y coordinate to return the print head to

    Returns:
        str: GCode command sequence for the return movement
    """
    return (
        f"G1 Y{y_return_position} F{y_feed_rate}\n"
        "VALVES_SET VALUES=0,0,0,0,0,0,0,0,0,0,0\n"
        f"G1 Y{y_return_position+1}\n"
        "FILL_HOPPER_ASYNC\n"
        "SET_SECOND_PASS\n"
        "G4 P3000\n"
    )

def layer_end_cmd(y_start_bed_pos: int) -> str:
    return (
        f"G1 Y{y_start_bed_pos}\n"
        "VALVES_SET VALUES=0,0,0,0,0,0,0,0,0,0,0\n"
        "G1 Y0\n"
    )

# a function that converts a G-code and extracts the coordinates of the matrix object
# the current_pos will contain the ending posision of the print head, so this can be used for the 
# next iteration
def convert_gcode_to_pattern(gcode: str, config: Config, current_pos: GCodeMove = GCodeMove(0,0,0,0)) -> Pattern:
    ps = (config.machine2pattern_coord(config.bed_parameters.x_size_mm),config.bed_parameters.y_size_mm)
    pattern = Pattern(ps)

    for line in iter(gcode.splitlines()):
        try:
            target_pos = GCodeMove.fromstring(line)
        except ValueError:
            continue
        if target_pos.X is None: target_pos.X = current_pos.X
        if target_pos.Y is None: target_pos.Y = current_pos.Y

        if target_pos.is_G1_command():
            tolerance = 1e-8
            if abs(target_pos.X - current_pos.X) > tolerance:
                logger.warning(f"Begin and end coordinates do not have the same X-value (current: {(current_pos.X, current_pos.Y, current_pos.E)}, target: {(target_pos.X, target_pos.Y, target_pos.E)})")
            elif abs(target_pos.Y - current_pos.Y) > 0:
                begin, end = (target_pos, current_pos) if target_pos.Y <= current_pos.Y else (current_pos, target_pos)
                pattern.add_line(config.machine2pattern_coord(begin.X), int(begin.Y), int(end.Y))
        current_pos.update(target_pos)


    return pattern
    
def convert_pattern_row_to_gcode(row: list[int]) -> str:
    if any(val > 0 for val in row):
        pass # just for debugging
    values = list_of_bits_to_list_of_int(row)
    output = "VALVES_SET VALUES="
    for v in values:
        output += f"{v},"
    return output[:-1] + '\n'


def convert_to_output(pattern: Pattern, layer: int, config: Config) -> str:
    """ takes in a pattern, and returns Asterix gcode 
    
    note that X is the position of the hopper, and Y is the position of the print head.
    The hopper moves oppostie to the print head
    """
    if pattern.get_number_of_rows() > (config.machine_dimensions.y_maximum_position - config.machine_dimensions.y_initial_position):
        raise ValueError("The pattern contains more entries than the size of print bed allows")

    EXPECTED_LEN_ONE_ENTRY = 71
    n = pattern.get_number_of_rows() * EXPECTED_LEN_ONE_ENTRY + 1
    output = layer_begin_cmd(layer, config.machine_dimensions.x_maximum_position, config.bed_parameters.deposition_rate)
    
    #when two axes move together, klipper sees this as a diagonal move, and we need to increase
    # the feed rate by sqrt(2) to maintain desired velocity of each axis separately
    v_combined = int(math.sqrt(2)*config.machine_dimensions.y_feed_rate)
    #v_combined = 8460 #temporary to force the value to be same as the output we want to compare it with for the test
    y_dest = config.machine_dimensions.y_initial_position
    x_dest = config.machine_dimensions.x_maximum_position - y_dest

    feedrate = v_combined
    #first stroke, x-axis moves 'down'wards, y-axis upwards

    set_valves = True
    for i, row in enumerate(pattern.T):
        output += f"G1 Y{y_dest} X{x_dest} F{feedrate}\n"

        if set_valves==True:
            set_valves = False
        else:
            set_valves = True
            #output += convert_pattern_row_to_gcode(extract_every_second_bit(row, True))
            output += convert_pattern_row_to_gcode(row[::2])
        # update destination position
        y_dest += 1
        x_dest = config.machine_dimensions.x_maximum_position - y_dest
        if x_dest < 0: # hopper arrived in home position
            x_dest = 0
            feedrate = config.machine_dimensions.y_feed_rate
        if y_dest > config.machine_dimensions.y_maximum_position:
            raise IndexError("Number of rows in pattern exceeds size of the print bed")
    
    # reached end of stroke
    output += layer_return_cmd(y_dest, config.machine_dimensions.y_feed_rate)
    set_valves = True
    #back stroke    
    for row in pattern.T[::-1]:
        feedrate = config.machine_dimensions.y_feed_rate
        output += f"G1 Y{y_dest}\n"

        if set_valves==True:
            set_valves = False
        else:
            set_valves = True
            #output += convert_pattern_row_to_gcode(extract_every_second_bit(row, False))
            output += convert_pattern_row_to_gcode(row[1::2])
    
        # update destination position
        y_dest -= 1

        if y_dest < config.machine_dimensions.y_initial_position:
            raise IndexError("Print head past initial position while pattern is not yet finished")        
    
    output += layer_end_cmd(config.machine_dimensions.y_initial_position)
    return output

def calculate_fill_percentage(pattern: Pattern) -> float:
    """
    Calculate the percentage of non-zero values in a 2D numpy array.
    
    Args:
        pattern: 2D numpy array
        
    Returns:
        float: Percentage of non-zero values (0-100)
    """
    total_elements = pattern.size
    non_zero_elements = np.count_nonzero(pattern)
    return (non_zero_elements / total_elements) * 100


def process_gcode(gcode: str, cfg: Config):
    """takes ins a gcode file, and process it line by line until finished
    it will output the processd gcode suitable for the machine
    """
    stats = {}

    layer_count_match = re.search(r';LAYER_COUNT:(\d+)', gcode)
    if not layer_count_match:
        raise ValueError("Could not find LAYER_COUNT in gcode")
    
    layer_count = int(layer_count_match.group(1))
    print(f"Found {layer_count} layers in gcode")
    stats["layers found"] = str(layer_count)
    stats["feedrate"] = str(cfg.machine_dimensions.y_feed_rate)
    output = print_begin_cmd(layer_count)
    
    # Find all layer indices by iterating once through the lines
    layer_indices = []
    for i, line in enumerate(gcode.splitlines()):
        if line.startswith(";LAYER:"):
            layer_indices.append(i)
    
    if len(layer_indices) != layer_count:
        raise ValueError(f"Found {len(layer_indices)} layers but expected {layer_count}")
    
    fill_factor = 0
    # Process each layer block using the line indices
    lines = gcode.splitlines()
    current_pos = GCodeMove(0,0,0,0)
    for i in range(layer_count):
        start_line = layer_indices[i]
        if i < layer_count - 1:
            end_line = layer_indices[i + 1]
            layer_block = "\n".join(lines[start_line:end_line])
        else:
            # Last layer - take rest of file
            layer_block = "\n".join(lines[start_line:])
            
        print(f"Processing layer {i+1}")
        pattern = convert_gcode_to_pattern(layer_block, cfg, current_pos)
        fill_factor += calculate_fill_percentage(pattern)
        output += convert_to_output(pattern, i, cfg)

    stats['Fill factor'] = fill_factor / layer_count
    output += print_end_cmd(layer_count)
    
    output_obj = {}
    output_obj['gcode'] = output
    output_obj['statistics'] = stats

    return output_obj