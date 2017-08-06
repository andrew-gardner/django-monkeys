# Time per view
if 0:
    print 'Querying...'
    if USER:
        print 'User: %s' % USER 
    else:
        print 'User: all'
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

    print 'Diffing...'
    deltas = []
    for utimes in times.values():
        utimes = sorted(utimes)
        #print utimes
        for i in xrange(1, len(utimes)):
            deltas.append((utimes[i] - utimes[i - 1]).total_seconds())

    print '%d entries' % entries
    deltas = sorted(deltas)
    print 'Min delta: %d sec' % min(deltas)
    print 'Max delta: %d sec' % max(deltas)
    # Average probably isn't a good measure since people leave
    # median maybe?
    avg = 1.0 * sum(deltas) / len(deltas)
    print 'Avg delta: %d sec' % avg
    median = deltas[len(deltas) / 2]
    print 'Median delta: %d sec' % median

    #entries = len(TypedDie.objects.all())
    ests = median * entries
    print 'Estimated time: %d sec (%s)' % (ests, sec2tstr(ests))

