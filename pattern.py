import logging
import numpy as np

logger = logging.getLogger(__name__)

class Pattern(np.ndarray[np.uint8]):
    """A pattern class that inherits from numpy.ndarray to represent a 2D printing pattern."""
    
    def __new__(cls, size: tuple[int, int]):
        # Create a new zero-filled array
        obj = np.zeros(size, dtype=np.uint8).view(cls)
        logger.debug("Initialized Pattern!")
        return obj

    def __array_finalize__(self, obj):
        # This method is called every time a new Pattern is created
        if obj is None: return

    def add_line(self, column: int, start_row: int, end_row: int):
        """Changes part of the pattern to ones following the column and start and end row provided"""
        
        logger.debug(f"adding line to pattern [{column},{start_row}:{end_row}]")
        if (start_row < 0 or end_row >= self.shape[1] or 
            column < 0 or column >= self.shape[0]):
            logger.warning(
                f"Attempt to set pattern out of bounds (requested [{column},"
                f"{start_row}:{end_row}], size: {self.shape}"
            )
        self[column, start_row:end_row] = 1
    
    def clear(self):
        """Resets the pattern to all zeros"""
        self.fill(0)

    def get_number_of_columns(self):
        """Returns the number of columns in the pattern"""
        return self.shape[0]
    
    def get_number_of_rows(self):
        """Returns the number of rows in the pattern"""
        return self.shape[1]