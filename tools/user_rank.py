# Ranking
if 0:
    print 'Querying...'
    subfreq = {}
    for td in TypedDie.objects.all():
        if not td.submitter:
            continue
        if not thedie(td):
            continue
        subfreq[td.submitter] = subfreq.get(td.submitter, 0) + 1

    print 'Printing...'
    for submitter, n in sorted(subfreq.iteritems(), key=vsort, reverse=True):
        print '% -20s %d' % (submitter, n)

