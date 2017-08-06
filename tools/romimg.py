'''
Utility file
See romdiff.py
'''

from PIL import Image

'''
Given byte offset and mask return image (col, row)
maskb: binary mask
maski: bitshi
'''
def bit_b2i(offset, maskb=None, maski=None):
    maskin = {
        0x80: 7,
        0x40: 6,
        0x20: 5,
        0x10: 4,
        0x08: 3,
        0x04: 2,
        0x02: 1,
        0x01: 0,
        }
    if maski is None:
        maski = maskin[maskb]
    biti = offset * 8 + maski
    #print biti
    # Each column has 16 bytes
    # Actually starts from right of image
    col = (32 * 8 - 1) - biti / (8 * 32)
    # 0, 8, 16, ... 239, 247, 255
    row = (biti % 32) * 8 + (biti / 32) % 8
    #print row
    return (col, row)

'''
Given image row/col return byte (offset, binary mask)
'''
bit_i2bm = {}
for offset in xrange(8192):
    for maski in xrange(8):
        col, row = bit_b2i(offset, maski=maski)
        bit_i2bm[(col, row)] = offset, 1 << maski
def bit_i2b(col, row):
    return bit_i2bm[(col, row)]

'''
Convert a bytearray ROM file into a row/col bit dict w/ image convention
'''
def romb2romi(romb):
    if len(romb) != 8192:
        raise ValueError()
    ret = {}

    for col in xrange(32 * 8):
        for row in xrange(32 * 8):
            offset, maskb = bit_i2b(col, row)
            if maskb > 0x80:
                raise ValueError()
            byte = romb[offset]
            bit = int(bool(byte & maskb)) ^ 1
            ret[(col, row)] = bit
    return ret

def bitmap(rom1, rom2, fn_out):
    BIT_WH = 32 * 8                                                                                                                                                                                                                                        
    im = Image.new("RGB", (BIT_WH, BIT_WH), "black")
    diffs = []
    for col in xrange(BIT_WH):
        for row in xrange(BIT_WH):
            b1 = rom1[(col, row)]
            b2 = rom2[(col, row)]
            if b1 != b2:
                c = (255, 0, 0)
                diffs.append((col, row, b1, b2))
            else:
                if b1:
                    c = (128, 128, 128)
                else:
                    c = (0, 0, 0)
            im.putpixel((col, row), c)
    im.save(fn_out)
    return diffs

