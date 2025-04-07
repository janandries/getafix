import bitstring
import numpy as np
import numpy.typing as npt

def extract_every_second_bit_from_byte(input: np.uint8, even_bits: bool = True) -> int:
    """Extract every second bit from a byte.
    
    Takes an input byte and extracts every second bit. If even_bits is True, extracts bits 0,2,4,6.
    If even_bits is False, extracts bits 1,3,5,7. The extracted bits are combined into a new byte,
    with each bit placed in order from least significant to most significant position.

    Args:
        input: Input byte to extract bits from
        even: If True, extract even-indexed bits (0,2,4,6). If False, extract odd-indexed bits (1,3,5,7).
            Defaults to False.

    Returns:
        An 8-bit integer containing the extracted bits combined
    """
    result = 0
    begin = 0 if even_bits else 1
    for i in range(begin, 8, 2):
        result |= ((int(input) >> i) & 1) << (i // 2)
    return result

def extract_every_second_bit(input: list[np.uint8], even_bits: bool = True) -> list[int]:
    l = len(input)
    output = []
    if l == 0:
        raise ValueError("List is empty")
    if l == 1:
        return extract_every_second_bit_from_byte(input[0], even_bits)
    if l % 2:
        l = l - 1
    for i in range(0, l, 2):
       result = extract_every_second_bit_from_byte(input[i], even_bits) + (extract_every_second_bit_from_byte(input[i+1], even_bits) << 4)
       output.append(result)
    
    if len(input)%2:
        output.append(extract_every_second_bit_from_byte(input[-1], even_bits))

    return output


def reverse_8_bits(n: np.uint8):
    # returns a bitstring with the bits reversed
    if (n < 256):
        b = format(n, '08b')
        b = bitstring.BitArray(bin=b[::-1])
        return b.uint
    else:
        raise(ValueError(f"Provided value is larger than 8 bits (value: {n} > 256)"))
    


def list_of_bits_to_list_of_int(bits: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
    """Convert a numpy array of bits to a numpy array of unsigned integers.
    
    Args:
        bits: numpy array of length n*8 containing 1s and 0s
        
    Returns:
        Numpy array of n unsigned integers, where each integer is created from 8 consecutive bits
    """
    if len(bits)%8:
        raise ValueError(f"length of input must be multiple of 8 (length is {len(bits)})")
    result = np.zeros(len(bits)//8, dtype=np.uint8)
    for i in range(0, len(bits), 8):
        val = 0
        for j in range(8):
            val |= (bits[i+j] << j)
        if val > 0:
            pass
        result[i//8] = reverse_8_bits(val)
    return result