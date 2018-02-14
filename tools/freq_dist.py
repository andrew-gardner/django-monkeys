# Solution frequency distribution

import sys
import os
sys.path.insert(0, os.path.dirname(__file__) + '/..')

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")
import django
django.setup()
from typer.models import Die, DieImage, TypedDie

import argparse
import ast
import re

from stats import *
import stats

def run(user, image, verbose=False):
    stats.USER = user
    stats.IMG = image

    buckets = {}

    print 'Querying...'
    for tdi, td in enumerate(TypedDie.objects.all()):

        if not interesting(td):
            if tdi % 256 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()
            continue
        if tdi % 256 == 0:
            sys.stdout.write('+')
            sys.stdout.flush()

        # td.typedField
        #addk(subfreq, td.submitter)
        k = str(td.dieImage.image)
        if k in buckets:
            m = buckets[k]
        else:
            m = {}
            buckets[k] = m
        tf = td.typedField.strip()
        addk(m, tf)
    print ' done'

    print 'Printing...'
    mfreq = {}
    for imgid, rfreq in sorted(buckets.iteritems(), key=vsort, reverse=True):
        if verbose:
            print '%s: %d freq' % (imgid, len(rfreq))
        addk(mfreq, len(rfreq))

    print 'Frequency distribution'
    for k, v in sorted(mfreq.iteritems()):
        print '%d: %d' % (k, v)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Solution frequency distribution')
    parser.add_argument('--verbose', action='store_true', help='verbose')
    parser.add_argument('--user', '-u', help='user filter')
    parser.add_argument('--image', '-i', help='image filter')
    args = parser.parse_args()

    run(user=args.user, image=args.image, verbose=args.verbose)

