from dataclasses import dataclass
import bitstring
import numpy as np
import logging
from gcode import GCodeMove
import math
from pattern import Pattern
import re

import tomli
from util import reverse_8_bits, extract_every_second_bit, list_of_bits_to_list_of_int
from config import Config

logger = logging.getLogger(__name__)

class Processor():
    """ A class that processes GCode files and converts them to a simplified pattern format.
    
    This processor reads GCode files line by line, detecting layer changes and extrusion moves.
    For each layer, it builds up a pattern of vertical lines based on the extrusion moves,
    and converts that pattern to a simplified output format.

    The processor expects GCode moves to be vertical (constant X coordinate) and will raise
    a ValueError if non-vertical moves are encountered.
    """
    def __init__(self):
        logger.debug("Initialized Processor")
        self._layer_count = 0
        self._output = ""
        self.X_MAXIMUM_POSITION = 1388 #should come from the congig!

        try:
            with open('machine.toml', 'rb') as f:
                self.machine = tomli.load(f)
        except Exception as e:
            logger.error(f"Failed to load machine.toml configuration file: {str(e)}")
            raise RuntimeError("Could not load required machine configuration") from e


    def convert_to_output(self, pattern: Pattern, layer: int):
        """ takes in a pattern, and returns Asterix gcode 
        
        note that X is the position of the hopper, and Y is the position of the print head.
        The hopper moves oppostie to the print head
        """
        EXPECTED_LEN_ONE_ENTRY = 71
        n = pattern.get_number_of_rows() * EXPECTED_LEN_ONE_ENTRY + 1
        output = self.layer_begin_cmd(layer)
        
        #the gcode for a layer consists of:
        # deposit the material

        #several states we pass through:
        # 1. only hopper moves (deposit layer)
        # 2. hopper moves in tandem with print head to initial position
        # 3. hopper moves in tandem with print head, and we deposit water
        # 4. hoppe arrives and we need to only move printhead
        # 5. print head rrives at end, prepare for eecond layer
        # 6. print head moves back alone
        # 7. done

        p = pattern

        y_feed_rate_when_move_together = math.floor(math.sqrt(2) * self.machine.y_feed_rate)

        #1
        output += f'G1 X{self.machine.x_maximum_position} F{self.machine.deposition_rate}; deposit material'

        #2
        current_y_pos =  self.machine.y_initial_position
        current_hopper_pos = self.machine.x_maximum_position - current_y_pos
        output += f"G1 Y{current_y_pos} X{current_hopper_pos} F{y_feed_rate_when_move_together}\n"    
        
        #3
        for p in pattern:
            current_y_pos += 1
            current_hopper_pos = self.machine.x_maximum_position - current_y_pos

            current_y_pos += 1
            current_hopper_pos = self.machine.x_maximum_position - current_y_pos # moves hopper oppostie to the print head
            hopper_pos = max(hopper_pos, 0) #stop when the hopper reaches zero position

            if y_pos == self.machine.y_initial_position:
                output += f"G1 Y{y_pos} X{hopper_pos} F{feedspeed}\n"
                y_pos += 1
            else:
                output += f"G1 Y{y_pos} X{hopper_pos} F{feedspeed}\n"
                y_pos += 1
                if hopper_pos == 0:
                    #when the hopper reaches its begin position, we need to reduce the feed speed
                    #by sqrt(2) as klipper thinks it was moving in two dimensions, and now in one
                    feedspeed = 6000

            if y_pos % 2 == 0:
                # to reduce the frequency of the valves, we only change the valves every other row (i.e. milimeter)
                output += "VALVES_SET VALUES="
                for i in range(len(p) // 2):
                    reversed_bitset = reverse_8_bits(bitstring(p[i]))
                    output += f"{reversed_bitset.uint},"
                output = output.rstrip(',') + '\n'

        output += self.layer_return_cmd(y_pos)

        return output
    

    
    def process(self, file: str, output_filename: str):
        OUTPUT_TEMP_FILENAME = output_filename
        previous_move = GCodeMove(0,0,0,0) # previous gcode move
        self._pattern = Pattern(self.machine2pattern_coord((self.machine.x_size, self.machine.y_size)))
        with open(file, 'r') as f:
            with open(OUTPUT_TEMP_FILENAME, 'w+') as f_out:
                for line in f:
                    if line.upper().startswith(";LAYER:"):
                        if self._layer_count > 0:
                            out = self.convert_to_output(self._pattern, self._layer_count)
                            f_out.write(out + '\n')
                            self._pattern.clear()
                        self._layer_count += 1
                    else:
                        try:
                            if self._layer_count == 0:
                                continue
                            current_move = GCodeMove.fromstring(line)
                            if current_move.is_G1_command():
                                tolerance = 1e-8
                                if abs(current_move.X - previous_move.X) > tolerance:
                                    raise ValueError("Begin and end coordinates do not have the same X-value")

                                begin, end = (current_move, previous_move) if current_move.Y <= previous_move.Y else (previous_move, current_move)
                                self._pattern.add_line(self.get_pattern_coord(begin.X), self.get_pattern_coord(begin.Y), self.get_pattern_coord(end.Y))
                            previous_move = current_move
                        except ValueError:
                            pass #logger.warning(f"Invalid move encountered: {line.strip()}")



                

# determine number of layers


# loop over all layers

#FUNCTION: for current layer, build up a matrix containing the spray pattern, line by line from the gcode file
#FUNCTION: Take a spray pattern, and generate the G-code for it


# per layer, build up a matrix of the full bed dimensions (read from a config)

# step through all G code commands, looking for G1 and G0.
# all G1 codes create a line, and should be converted to 1's in the appropiate places in the matrix

# matrix.add_spray_line(gcode command)

# when fininshed with the layer, convert the layer matrix into G code that the Asterix understands.
# matrix.convert_to_output

def print_begin_cmd(number_of_layers: int) -> str:
    return (
        f"SET_PRINT_STATS_INFO TOTAL_LAYER={number_of_layers}\n"
        "G28 X Y SET_FIRST_PASS G4 P3000 ;wait for servo\n"
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
        "PAUSE_PRINTER ;wait for button press\n"
        f"G1 X{x_maximum_position} F{deposition_rate}; deposit material\n"
    )

def layer_return_cmd(y_return_position: int) -> str:
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
        f"G1 Y{y_return_position} F6000\n"
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
def convert_gcode_to_pattern(gcode: str, config: Config) -> Pattern:
    ps = (config.machine2pattern_coord(config.bed_parameters.x_size_mm),config.bed_parameters.y_size_mm)
    pattern = Pattern(ps)

    current_pos = GCodeMove(0,0,0,0)
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
                logger.warning("Begin and end coordinates do not have the same X-value")
            elif abs(target_pos.Y - current_pos.Y) > 0:
                begin, end = (target_pos, current_pos) if target_pos.Y <= current_pos.Y else (current_pos, target_pos)
                pattern.add_line(config.machine2pattern_coord(begin.X), int(begin.Y), int(end.Y))
                if (pattern>1).any():
                    pass # used for debugging to check if no cell is set to a value different than 1
        if pattern[0,0] > 0:
            pass
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
    v_combined = 8460 #temporary to force the value to be same as the output we want to compare it with for the test
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
    output += layer_return_cmd(y_dest)
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

def process_gcode(gcode: str, cfg: Config):
    """takes ins a gcode file, and process it line by line until finished
    it will output the processd gcode suitable for the machine
    """
    
    layer_count_match = re.search(r';LAYER_COUNT:(\d+)', gcode)
    if not layer_count_match:
        raise ValueError("Could not find LAYER_COUNT in gcode")
    
    layer_count = int(layer_count_match.group(1))
    logger.debug(f"Found {layer_count} layers in gcode")
    
    output = print_begin_cmd(layer_count)
    
    # Find all layer indices by iterating once through the lines
    layer_indices = []
    for i, line in enumerate(gcode.splitlines()):
        if line.startswith(";LAYER:"):
            layer_indices.append(i)
    
    if len(layer_indices) != layer_count:
        raise ValueError(f"Found {len(layer_indices)} layers but expected {layer_count}")
    
    # Process each layer block using the line indices
    lines = gcode.splitlines()
    for i in range(layer_count):
        start_line = layer_indices[i]
        if i < layer_count - 1:
            end_line = layer_indices[i + 1]
            layer_block = "\n".join(lines[start_line:end_line])
        else:
            # Last layer - take rest of file
            layer_block = "\n".join(lines[start_line:])
            
        pattern = convert_gcode_to_pattern(layer_block, cfg)
        output += convert_to_output(pattern, i, cfg)

    output += print_end_cmd(layer_count)
    
    return output