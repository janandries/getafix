import pytest
from gcode import GCodeMove


def test_gcodemove_init():
    g = GCodeMove(0, 0, 0, 0)
    assert g.is_G1_command() == False

    g = GCodeMove.fromstring("G1 X5")
    assert g.is_G1_command() == True

    g = GCodeMove.fromstring("G1 X5 E2")
    assert g.is_G1_command() == True

    g = GCodeMove.fromstring("G1 Y-12")
    assert g.is_G1_command() == True

    g = GCodeMove.fromstring("G0 Y0 Z4")
    assert g.X == None
    assert g.Y == 0
    assert g.Z == 4
    assert g.E == None
    assert g.is_G1_command() == False

    with pytest.raises(ValueError):
        g = GCodeMove.fromstring("M123 X3 Y5")
    
    with pytest.raises(ValueError):
        g = GCodeMove.fromstring("G2 X3 Y5")
    
