from util import reverse_8_bits, list_of_bits_to_list_of_int, extract_every_second_bit
import bitstring
import numpy as np

def test_extract_every_second_bit():
    r = extract_every_second_bit([0xAA, 0xAA, 0xAA, 0xAA, 0xAA], even_bits=False)
    assert r == [0xff, 0xff, 0x0f]

    r = extract_every_second_bit([0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA], even_bits=False)
    assert r == [0xff, 0xff, 0xff]

    r = extract_every_second_bit([0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA], even_bits=True)
    assert r == [0x00, 0x00, 0x00]

    r = extract_every_second_bit([0x55, 0x55, 0x55, 0x55, 0x55, 0x55], even_bits=True)
    assert r == [0xff, 0xff, 0xff]

    r = extract_every_second_bit([0x55, 0x55, 0x55, 0x55, 0x55, 0x55], even_bits=False)
    assert r == [0x00, 0x00, 0x00]

    full_data = [0xD4, 0x8C, 0x2E, 0x9F, 0x2C, 0x3B, 0x2E, 0x02, 0x59, 0xAE, 0x1C] # <- MSB first
    uneven_bits = [0x08, 0xA7, 0xB6, 0x77, 0x12, 0xF2] # <- idem
    even_bits =  [0x0E, 0x22, 0x72, 0x52, 0x0D, 0x26] # <- idem
    full_data.reverse(), even_bits.reverse(), uneven_bits.reverse() # <- so we reverse to have LSB first
    r = extract_every_second_bit(full_data, even_bits=False)
    assert r == uneven_bits

    r = extract_every_second_bit(full_data, even_bits=True)
    assert r == even_bits

def test_reverse_bits2():
    assert reverse_8_bits(8) == 16
    assert reverse_8_bits(255) == 255
    assert reverse_8_bits(170) == 85  # 10101010 -> 01010101
    assert reverse_8_bits(15) == 240  # 00001111 -> 11110000
    assert reverse_8_bits(240) == 15  # 11110000 -> 00001111
    assert reverse_8_bits(0) == 0
    assert reverse_8_bits(1) == 128


def test_list_of_bits_to_list_of_int():
    # Test basic conversion
    bits = np.array([1,0,1,0,1,0,1,0])  # 170 in binary
    assert np.array_equal(list_of_bits_to_list_of_int(bits), np.array([170], dtype=np.uint8))

    # Test multiple bytes
    bits = np.array([1,1,1,1,0,0,0,0, 0,0,0,0,1,1,1,1])  # [240, 15]
    assert np.array_equal(list_of_bits_to_list_of_int(bits), np.array([240, 15], dtype=np.uint8))

    # Test all zeros
    bits = np.array([0,0,0,0,0,0,0,0])
    assert np.array_equal(list_of_bits_to_list_of_int(bits), np.array([0], dtype=np.uint8))

    # Test all ones 
    bits = np.array([1,1,1,1,1,1,1,1])
    assert np.array_equal(list_of_bits_to_list_of_int(bits), np.array([255], dtype=np.uint8))

    # Test alternating bytes
    bits = np.array([1,0,1,0,1,0,1,0, 0,1,0,1,0,1,0,1])  # [170, 85]
    assert np.array_equal(list_of_bits_to_list_of_int(bits), np.array([170, 85], dtype=np.uint8))