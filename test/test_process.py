import pytest
import numpy as np
from config import Config
from process import convert_pattern_row_to_gcode, convert_to_output, process_gcode
from pattern import Pattern

config_data = {
    'machine_dimensions': {
        'x_initial_position': None,
        'x_maximum_position': None,
        'y_initial_position': None,
        'y_maximum_position': None,
        'y_feed_rate': None
    },
    'nozzle_configuration': {
        'total_nozzles': None,
        'nozzles_per_manifold': None,
        'number_of_passes': None
    },
    'bed_parameters': {
        'x_size_mm': None,
        'y_size_mm': None,
        'resolution_mm': None,
        'deposition_rate': None
    }
}

def test_pattern_size():
    config_data  = {
    'bed_parameters': {
        'x_size_mm': 20,
        'y_size_mm': 20,
        'resolution_mm': 5
    }
    }

    conf = Config.from_dict(config_data)
    p = convert_gcode_to_pattern("", conf)
    assert p.shape == (4, 20)

    config_data['bed_parameters']['x_size_mm'] = 24
    conf = Config.from_dict(config_data)
    p = convert_gcode_to_pattern("", conf)
    assert p.shape == (4, 20)

def test_input_output():    
    cfg = Config.from_file('machine.toml')

    TEST_INPUT_FILENAME = "test/test_2_input.gcode"
    TEST_OUTPUT_FILENAME = "test/test_2_output.test"
    TEST_TRUTH_FILENAME = "test/test_2_output.gcode"
    
    with open(TEST_INPUT_FILENAME, 'r') as f:
        input_gcode = f.read()
        output = process_gcode(input_gcode,cfg)

    # write output to file so we can also manually compare
    with open(TEST_OUTPUT_FILENAME, 'w') as file:
        file.write(output)

    #compare both files
    line_nr = -1
    with open(TEST_TRUTH_FILENAME, 'r') as truth:
        output_lines = iter(output.splitlines(keepends=True))
        while True:
            line_nr+=1
            t = truth.readline()
            o = next(output_lines)
            if t == "" and o == "": 
                break
            assert t == o


from process import convert_gcode_to_pattern
def test_convert_gcode_to_pattern():
    config_data  = {
    'bed_parameters': {
        'x_size_mm': 20,
        'y_size_mm': 20,
        'resolution_mm': 5
    }
    }

    conf = Config.from_dict(config_data)
    gcode = """G0 X0 Y0
G1 X0 Y20
G0 X19 Y20
G1 X19 Y0 F1500 E117.56598
G0 F3600 X30 Y50
G0 F1800 X30 Y200
G0 F3600 X5 Y0"""

    p = convert_gcode_to_pattern(gcode, conf)
    r = np.zeros((4,4))
    r[0,:]=1
    r[-1,:]=1
    assert (p==r).all()



from process import convert_gcode_to_pattern
def test_convert_gcode_to_pattern_2():
    config_data  = {
    'bed_parameters': {
        'x_size_mm': 20,
        'y_size_mm': 20,
        'resolution_mm': 5
    }
    }

    conf = Config.from_dict(config_data)
    gcode = """G0 X19 Y20
G1 X19 Y0"""

    p = convert_gcode_to_pattern(gcode, conf)
    r = np.zeros((4,4))
    r[-1,0:4]=1
    assert (p==r).all()


def test_convert_pattern_row_to_gcode():
    s1 = convert_pattern_row_to_gcode(np.zeros(88))
    assert s1 == "VALVES_SET VALUES=0,0,0,0,0,0,0,0,0,0,0"

    s2 = convert_pattern_row_to_gcode(np.ones(88))
    assert s2 == "VALVES_SET VALUES=255,255,255,255,255,255,255,255,255,255,255"

    r3 = np.concatenate((np.ones(44), np.zeros(44)))
    s3 = convert_pattern_row_to_gcode(r3)
    assert s3 == "VALVES_SET VALUES=255,255,255,255,255,240,0,0,0,0,0"

    r4 = np.array([1,1,0,1,1,1,0,0, 1,1,0,1,1,0,0,1, 0,1,1,0,0,1,1,1, 1,1,0,1,0,0,1,1])
    assert len(r4) == 32        
    s4 = convert_pattern_row_to_gcode(r4)
    assert s4 == "VALVES_SET VALUES=220,217,103,211" # or: 59,155,230,203?probably not

    
def test_convert_to_output():
    config_data  = {
    'bed_parameters': {
        'x_size_mm': 20,
        'y_size_mm': 20,
        'resolution_mm': 5
    },
    'machine_dimensions': {
        'x_initial_position': 0,
        'x_maximum_position': 1388,
        'y_initial_position' : 118,
        'y_maximum_position' : 1462,
        'y_feed_rate' : 6000
    }
    }

    cfg = Config.from_dict(config_data)

    # create a pattern
    arr = np.array([[1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1],
                    [1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,1,1,1]])
    p = arr.view(Pattern)
    
    out = convert_to_output(p, 1, cfg)
    print(out)