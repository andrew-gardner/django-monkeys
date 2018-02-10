#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/..')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")
import django
django.setup()
from typer.models import TypedDie

import argparse
import ast
import re
import json

from PIL import Image, ImageDraw

'''
Each are 8x8
'''
warnings = []
warnings_field = {}
def romwf(rom, gcol, grow, fieldm, overrides):
    absrow = grow * 8
    abscol = gcol * 8
    entries = sum(fieldm.values())

    if 0:
        if (gcol, grow) != (0, 0):
            return
        print fieldm

    # Vote on all individual bits
    # if 4/5 match consider it a win
    def pervote1(fieldm):
        ret = [None] * (8 * 8)
        # If 4/5 of any individual bits consider it good
        for biti in xrange(8 * 8):
            freqa = {}
            for view, freq in fieldm.iteritems():
                bit = view[biti]
                freqa[bit] = freqa.get(bit, 0) + freq
            if len(freqa) == 1:
                for k, v in fieldm.iteritems():
                    bit = k
            elif len(freqa) == 2:
                for k, v in fieldm.iteritems():
                    if v == entries - 1 or (okay() and v == entries - 2):
                        bit = k
                    elif v == 1:
                        continue
                    else:
                        return None
            else:
                return None
            if bit not in '01':
                return None
            ret[biti] = bit
        ret = ''.join(ret)
        if len(ret) != 64:
            print ret
            raise ValueError()
        return ret

    def pervote1m(fieldm):
        ret = [None] * (8 * 8)
        # If 4/5 of any individual bits consider it good
        for biti in xrange(8 * 8):
            freqa = {}
            for view, freq in fieldm.iteritems():
                bit = view[biti]
                freqa[bit] = freqa.get(bit, 0) + freq

            if len(freqa) == 1:
                for k, _v in freqa.iteritems():
                    bit = k
            elif len(freqa) == 2:
                bit = '?'
                for k, v in fieldm.iteritems():
                    if v == entries - 1 or (okay() and v == entries - 2):
                        bit = k
            else:
                bit = '?'
            ret[biti] = bit

        ret = ''.join(ret)
        if len(ret) != 64:
            print ret
            raise ValueError()
        return ret

    def warn(gcol, grow, msg):
        print 'WARNING: %s, %s: %s' % (gcol, grow, msg)
        warnings.append((gcol, grow))
        warnings_field[(gcol, grow)] = pervote1m(fieldm)

    override = overrides.get((gcol, grow), None)
    if override and override != 'ok':
        print 'NOTE: overriding %s, %s' % (gcol, grow)
        field = overrides[(gcol, grow)]

    else:
        def okay():
            return overrides.get((gcol, grow), None) == 'ok'

        '''
        This is probably too aggressive
        Sometimes a user inputs a single ?
        '''
        if 0:
            for k, v in fieldm.iteritems():
                if '?' in k:
                    warn(gcol, grow, '? %s' % (fieldm.values(),))
                    return

        # Vote on best field
        # Easy case: all the same
        field = None
        pervote_res = field = pervote1(fieldm)
        if len(fieldm) == 1:
            field = fieldm.keys()[0]
        elif pervote_res:
            field = pervote_res
        elif len(fieldm) == 2:
            # Alarm if its not a single error
            for k, v in fieldm.iteritems():
                if v == entries - 1 or (okay() and v == entries - 2):
                    field = k
                elif v == 1:
                    continue
                elif not okay():
                    warn(gcol, grow, 'freq2 %s' % (fieldm.values(),))
                    return
        elif len(fieldm) == 3:
            # Alarm if its not two single errors
            for k, v in fieldm.iteritems():
                # These are suspicious
                # maybe best to review them
                if okay():
                    if v == entries - 2:
                        field = k
                else:
                    warn(gcol, grow, 'freq3 %s' % (fieldm.values(),))
                    return
        else:
            warn(gcol, grow, 'freq %s' % (fieldm.values(),))
            return

    if '?' in field:
        warn(gcol, grow, '? field %s' % (fieldm.values(),))
        return

    if not field:
        warn(gcol, grow, 'bad field %s' % (fieldm.values(),))
        return

    field = field.strip().replace(' ', '').replace('\n', '')

    for frow in xrange(8):
        for fcol in xrange(8):
            c = field[frow * 8 + fcol]
            bit = {'0': 0, '1': 1}.get(c, None)
            if bit is None:
                warn(gcol, grow, 'char %s' % (c,))
                return
            #rom[(absrow + frow) * 32 + abscol + fcol] = bit
            romw(rom, abscol + fcol, absrow + frow, bit)

def romw(rom, col, row, v):
    '''Write ROM state'''
    if col >= 32 * 8 or row >= 32 * 8:
        raise ValueError('%s, %s' % (col, row))
    rom[row * 32 * 8 + col] = v

def romr(rom, col, row):
    '''Read ROM state'''
    if col >= 32 * 8 or row >= 32 * 8:
        raise ValueError('%s, %s' % (col, row))

    try:
        return rom[row * 32 * 8 + col]
    except:
        print('%s, %s' % (col, row))
        raise

def isimg(td, img_want):
    '''Is this for the image we are working on?'''
    return str(td.dieImage.image).find(img_want) == 0

def get_dist(img_want):
    '''
    Get typed bits distribution per field
    Get a distribution for a position via ret[(gcol, grow)][(fcol, frow)]
    '''
    dist = {}
    matches = 0
    for tdi, td in enumerate(TypedDie.objects.all()):
        if not isimg(td, img_want):
            if tdi % 256 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
            continue
        if tdi % 256 == 0:
            sys.stdout.write('+')
            sys.stdout.flush()

        # sega_315-5571_xpol/sega_315-5571_xpol_01_09.png
        fn = str(td.dieImage.image)
        m = re.match(r'.*/(.*)_([0-9]*)_([0-9]*).png', fn)
        if not m:
            raise Exception()
        #print fn
        matches += 1
        #img = m.group(1)
        #if img != img_want:
        #    continue
        col = int(m.group(2))
        row = int(m.group(3))
        #print row, col
        if (col, row) in dist:
            distv = dist[(col, row)]
        else:
            distv = {}
            dist[(col, row)] = distv
        typed = str(td.typedField).strip().replace('\n', '')
        distv[typed] = distv.get(typed, 0) + 1
    #print 'Matches: %d' % matches
    if matches != (5 * 32 * 32):
        raise ValueError()
    return dist

def dist_by_bits(dist):
    '''Return a per bit instead of per solution dist'''
    ret = {}
    for solution, frequency in dist.iteritems():
        fi = 0
        for frow in xrange(8):
            for fcol in xrange(8):
                pos_freqs = ret.setdefault((fcol, frow), {})
                bitchar = solution[fi]
                pos_freqs[bitchar] = pos_freqs.setdefault(bitchar, 0) + frequency
                fi += 1
    return ret

def im_roi(icol, irow):
    '''Get an ROI for just one bit in a task image'''
    if icol >= 8 or irow >= 8:
        raise ValueError()

    imwh = 14
    xmin = 1 + 14 * icol
    ymin = 1 + 14 * irow
    # The crop rectangle, as a (left, upper, right, lower)-tuple.
    crop = (xmin, ymin, xmin + imwh - 1, ymin + imwh - 1)
    #return im_full.crop(crop)
    return crop

def save_txt(rom, f):
    '''Save ROM state to file as .txt representing image layout'''
    # FIXME: generate these
    cols = 32 * 8
    rows = 32 * 8

    ret = ''
    for row in xrange(rows):
        for col in xrange(cols):
            if col % 8 == 0 and col:
                f.write(' ')
            f.write(str(romr(rom, col, row)))
        f.write('\n')
        if row % 8 == 0 and row:
            f.write('\n')
    return ret

# XXX: too many open files without ulimit
# maybe change to gen_images
# Load images
load_images_cache = {}
def load_images(img_name, toload):
    for (gcol, grow) in toload:
        load_images_cache[(gcol, grow)] = get_image(img_name, gcol, grow)
    return load_images_cache

def get_image(img_name, gcol, grow):
    fn = 'static/%s/%s_%02d_%02d.png' % (img_name, img_name, gcol, grow)
    return Image.open(fn)

def gen_warning_images(out_dir, img_name):
    print 'Generating warning images'
    images = load_images(img_name, warnings)

    # Mask
    #print images.keys()
    #print warnings_field.keys()
    for (gcol, grow), field in warnings_field.iteritems():
        im = images[(gcol, grow)]
        d = ImageDraw.Draw(im)
        for frow in xrange(8):
            for fcol in xrange(8):
                c = field[frow * 8 + fcol]
                if c not in '01':
                    roi = im_roi(fcol, frow)
                    d.rectangle(roi, fill=None, outline=(0xFF, 0xFF, 0))

    # Save
    for (gcol, grow), im in images.iteritems():
        im.save(os.path.join(out_dir, '%02d_%02d_m.png' % (gcol, grow)))

def gen_cv_images(meta_dir, img_name, dist, rom):
    print 'Generating CV images'
    #images = load_images(img_name, dist)

    meta_bits = {}
    for (gcol, grow), field in dist.iteritems():
        field_bits = dist_by_bits(field)
        #im = images[(gcol, grow)]
        im = get_image(img_name, gcol, grow)
        for frow in xrange(8):
            arow = grow * 8 + frow
            for fcol in xrange(8):
                acol = gcol * 8 + fcol
                roi = im_roi(fcol, frow)
                if meta_dir:
                    bitfn = "%02dgc-%02dgr_%02dfc-%02dfr.png" % (gcol, grow, fcol, frow)
                    meta_bit = {
                        # Global absolute coordinates
                        'col': acol,
                        'row': arow,
                        # Global tile coordinates
                        'gcol': gcol,
                        'grow': grow,
                        # Field (within a tile) coordinates
                        'frow': frow,
                        'fcol': fcol,
                        # Answer frequency distribution like
                        # {'0': 3, '1': 1, '?': 1}
                        "dist": field_bits[(fcol, frow)],
                        "best": romr(rom, acol, arow),
                        }
                    #print meta_bit
                    imc = im.crop(roi)
                    imc.save(os.path.join(meta_dir, "bit", bitfn))
                    imc.close()
                    meta_bits[bitfn] = meta_bit
        im.close()
    return meta_bits

def run(img_name, overrides=None, fn_out=None, meta_dir=None):
    if not overrides:
        overrides = {}

    # Reassemble the ROM
    print 'Assemble test'
    # 32 x 32, 8 x 8
    # row major order
    # Contains only 0/1 as integers
    rom = [None] * 8192 * 8

    print 'Querying...'
    dist = get_dist(img_name)
    print ' done'

    if meta_dir:
        if not os.path.exists(meta_dir):
            os.mkdir(meta_dir)
        if not os.path.exists(meta_dir + '/bit'):
            os.mkdir(meta_dir + '/bit')
    meta = {
        "meta": {
            "source": "django-monkeys/db2txt",
            "override": str(overrides),
            "img": img_name,
        },
        #"bit": meta_bits
    }

    for (col, row), fields in sorted(dist.iteritems()):
        romwf(rom, col, row, fields, overrides=overrides)

    # warning images trashes, run first
    if meta_dir:
        meta['bit'] = gen_cv_images(meta_dir, img_name, dist, rom)

    if warnings:
        print 'Warning template (%d)' % len(warnings)
        for (gcol, grow), field in sorted(warnings_field.iteritems()):
            #if (gcol, grow) != 0, 0:
            #    continue
            print '    (%d, %d): """' % (gcol, grow)
            for frow in xrange(8):
                base = frow * 8
                print '        %s' % (field[base:base+8],)
            print '    """,'

        out_dir = 'db2bin/%s' % img_name
        os.path.exists(out_dir) or os.mkdir(out_dir)

        gen_warning_images(out_dir, img_name)

        raise Exception("Resolve warnings before continuing")

    if not fn_out:
        fn_out = '%s_cs.txt' % img_name
    print 'Writing %s' % fn_out
    save_txt(rom, open(fn_out, 'w'))

    if meta_dir:
        json.dump(meta, open(os.path.join(meta_dir, 'meta.json'), 'w'),
                  sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract ROM .bin from monkey DB')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose')
    parser.add_argument('--cf', '-c', help='Correction file')
    parser.add_argument('--meta', '-m', help='Output CV metadata training file to given directory')
    parser.add_argument('image', help='Image file to process (ex: sega_315-5571_xpol)')
    parser.add_argument('fn_out', nargs='?', default=None, help='Output file name')
    args = parser.parse_args()

    overrides = None
    if args.cf:
        overrides = ast.literal_eval(open(args.cf, 'r').read())
    run(img_name=args.image, overrides=overrides, fn_out=args.fn_out, meta_dir=args.meta)
