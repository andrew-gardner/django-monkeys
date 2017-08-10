# Solution frequency distribution
if 0:
    buckets = {}

    print 'Querying...'
    for td in TypedDie.objects.all():
        if not interesting(td):
            continue

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

    print 'Printing...'
    mfreq = {}
    for imgid, rfreq in sorted(buckets.iteritems(), key=vsort, reverse=True):
        print '%s: %d freq' % (imgid, len(rfreq))
        addk(mfreq, len(rfreq))

    print 'Frequency distribution'
    for k, v in sorted(mfreq.iteritems()):
        print '%d: %d' % (k, v)

