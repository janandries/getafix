import math
from typing import Optional

class GCodeMove:
    """A class representing a G-code movement command (G0 or G1).

    This class handles parsing and storing G-code movement commands with X, Y, Z, and E parameters.
    It supports both travel moves (G0) and extrusion moves (G1).
    """

    def __init__(self, x: float = None, y: float = None, z: float = None, e: float = None, extrusion_move: bool = False):
        """Initialize a GCodeMove with optional X, Y, Z and E coordinates.

        Args:
            x (float, optional): X-axis position. Defaults to None.
            y (float, optional): Y-axis position. Defaults to None.
            z (float, optional): Z-axis position. Defaults to None.
            e (float, optional): Extruder position. Defaults to None.
        """
        self.X = x
        self.Y = y
        self.Z = z
        self.E = e
        self.extrusion_move = extrusion_move

    @classmethod
    def fromstring(cls, string: str):
        """Create a GCodeMove instance from a G-code command string.

        Args:
            string (str): G-code command string starting with G0 or G1

        Returns:
            GCodeMove: New instance with parsed coordinates

        Raises:
            ValueError: If command doesn't start with G0/G1 or has no parameters
        """
        if not (string.startswith('G0') or string.startswith('G1')):
            raise ValueError("Supplied gcode command must be starting with G0 or G1")

        parts = string.split()
        x, y, z, e = None, None, None, None
        at_least_one_parameter = False

        for part in parts[1:]:
            if part.startswith('X'):
                x = float(part[1:])
                at_least_one_parameter = True
            elif part.startswith('Y'):
                y = float(part[1:])
                at_least_one_parameter = True
            elif part.startswith('Z'):
                z = float(part[1:])
                at_least_one_parameter = True
            elif part.startswith('E'):
                e = float(part[1:])
                at_least_one_parameter = True

        if not at_least_one_parameter:
            raise ValueError("Supplied gcode command needs to have at least a single parameter (X, Y, Z or E)")

        return cls(x, y, z, e, string.startswith('G1'))

    def is_G1_command(self) -> bool:
        """Check if this move includes extrusion.

        Returns:
            bool: True if the original G-code command was an extrusion move (i.e. G1), False otherwise
        """
        return self.extrusion_move
    
    def update(self, move):
        if (move.X):
            self.X = move.X
        if (move.Y):
            self.Y = move.Y
        if (move.Z):
            self.Z = move.Z
        if (move.E):
            self.E = move.Z