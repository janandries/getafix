
from old.processmanager import PrintHead
import pytest, bitstring

def test_printhead_constructor():
    ph = PrintHead(5, 11, 8)
    assert ph.nr_of_nozzles() == 88

def test_printhead_block_indices():
    ph = PrintHead(5, 11, 8)
    block_index, block_offset = ph.get_block_indices(0)
    assert block_index == 0
    assert block_offset == 0
    
    block_index, block_offset = ph.get_block_indices(30)
    assert block_index == 0
    assert block_offset == 6
    
    block_index, block_offset = ph.get_block_indices(860)
    assert block_index == 21
    assert block_offset == 4

