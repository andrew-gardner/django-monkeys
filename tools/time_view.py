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

def run(user):
    global USER
    USER = user
    stats.USER = user

    # Time per view
    print 'Querying...'
    
    users = None
    if USER == '*':
        print 'User: all individual'
        users = active_users()
        print '%d active users' % len(users)
    elif USER:
        print 'User: %s' % USER 
    else:
        print 'User: all aggregate'
    times = {}
    entries = 0
    for td in TypedDie.objects.all():
        if not interesting(td):
            continue
        #subfreq[td.submitter] = subfreq.get(td.submitter, 0) + 1
        #print date_mils(td.submitDate)
        #delta = td.submitDate - td.submitDate
        #print delta.total_seconds()
        k = str(td.submitter)
        if k in times:
            l = times[k]
        else:
            l = []
            times[k] = l
        l.append(td.submitDate)
        entries += 1

    def run_user(user):
        deltas = []
        for this_user, utimes in times.iteritems():
            if user and user != this_user:
                continue
            utimes = sorted(utimes)
            #print utimes
            for i in xrange(1, len(utimes)):
                deltas.append((utimes[i] - utimes[i - 1]).total_seconds())
        deltas = sorted(deltas)
        #print 'Diffing...'

        print '%d entries' % entries
        if deltas:
            print 'Min delta: %d sec' % min(deltas)
            #print 'Max delta: %d sec' % max(deltas)
            # Average probably isn't a good measure since people leave
            # median maybe?
            #avg = 1.0 * sum(deltas) / len(deltas)
            #print 'Avg delta: %d sec' % avg
            median = deltas[len(deltas) / 2]
            print 'Median delta: %d sec' % median

            #entries = len(TypedDie.objects.all())
            ests = median * entries
            print 'Estimated time: %d sec (%s)' % (ests, sec2tstr(ests))

    if USER == '*':
        for auser in times.keys():
            print
            print 'User: %s' % auser
            run_user(auser)
    else:
        run_user(user)
    

run(USER)


