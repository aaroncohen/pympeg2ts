def get_bit(byteval, idx):
    return min((byteval & (256 >> idx)), 1)


def tobits(s):
    result = []
    for c in s:
        if type(c) is not int:
            c = ord(c)
        bits = bin(c)[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


def frombits(bits, pad_to_bytes=1):
    chars = []
    if pad_to_bytes:
        bits_len = len(bits)
        nearest = round_up_to_nearest(bits_len, base=pad_to_bytes*8)
        if bits_len != nearest:
            bits.reverse()
            bits = [bits[i] if i < bits_len else 0 for i in xrange(nearest)]
            bits.reverse()

    for b in range(len(bits) / 8):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)


def round_up_to_nearest(x, base=8):
    if x % base:
        return x + (base - x % base)
    else:
        return x


class Lazy(object):
    def __init__(self, calculate_function):
        self._calculate = calculate_function

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        setattr(obj, self._calculate.func_name, value)
        return value
