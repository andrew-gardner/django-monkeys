# backpropagate ROM into image

'''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/..')

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")
import django
django.setup()
from typer.models import Die, DieImage, TypedDie
'''

from romimg import *

import argparse
import os
import re

def run(rom1_fn, rom2_fn, fn_out):
    img_fn = 'sega_315-5677_xpol'

    rom1b = bytearray(open(rom1_fn, 'r').read())
    rom2b = bytearray(open(rom2_fn, 'r').read())
    print 'Converting to image layout...'
    rom1i = romb2romi(rom1b)
    rom2i = romb2romi(rom2b)
    dir_out = 'romdiff'
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    diffs = bitmap(rom1i, rom2i, fn_out)

    if 1:
        for diff in diffs:
            col, row, b1, b2 = diff
            print 'x%d, y%d, CS: %d, C0: %d' % (col, row, b1, b2)
            off, mask = bit_i2b(col, row)
            print '  Offset 0x%04X, mask 0x%02X' % (off, mask)
            vg_col = col / 8
            vl_col = col % 8
            vg_row = row / 8
            vl_row = row % 8
            print '  http://cs.sipr0n.org/static/%s/%s_%02d_%02d.png @ col %d, row %d' % (img_fn, img_fn, vg_col, vg_row, vl_col, vl_row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visually diff two .bin in original image layout, printing differences')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose')
    parser.add_argument('rom1', help='ROM1 file name')
    parser.add_argument('rom2', help='ROM2 file name')
    parser.add_argument('out', nargs='?', default=None, help='Output file name')
    args = parser.parse_args()

    fn_out = args.out
    if not fn_out:
        fn_out = 'out.png'
    run(rom1_fn=args.rom1, rom2_fn=args.rom2, fn_out=fn_out)

