import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")
import django
django.setup()
from typer.models import Die, DieImage, TypedDie
import datetime
import re
import sys
from PIL import Image

IMG = 'sega_315-5572'
USER = None
#USER = 'brizzo'
#USER = 'sparkyman215'


def thesub(td):
    return not USER or str(td.submitter) == USER

def thedie(td):
    k = str(td.dieImage.image)
    #print k
    return k.find(IMG) == 0

def interesting(td):
    return td.submitter and thesub(td) and thedie(td)

def defk(m, k, default):
    if not k in m:
        m[k] = default

def addk(m, k):
    m[k] = m.get(k, 0) + 1

vsort = lambda x: x[1]

def date_mils(dt):
    return (dt - datetime.datetime(1970,1,1)).total_seconds()

print 'Image: %s' % IMG

def sec2tstr(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)



