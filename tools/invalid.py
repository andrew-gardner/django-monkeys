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
http://cs.sipr0n.org/typer/Sega_315-5571_xpol/adminSummary/467/

xwins
17-07-24
1:11 

says its length 0
weird
'''

print 'Querying...'
for td in TypedDie.objects.all():
    if USER and str(td.submitter) != USER:
        continue
    k = str(td.dieImage.image)
    if k.find('sega_315-5571_xpol_14_18.png') < 0:
        continue
    print 'got it'
    tf = str(td.typedField)
    print len(tf)
    print tf

