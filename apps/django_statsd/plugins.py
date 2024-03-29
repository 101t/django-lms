import logging
import os

NOSE = False
try:
    from nose.plugins.base import Plugin
    NOSE = True
except ImportError:
    class Plugin:
        pass

from .clients import statsd

log = logging.getLogger(__name__)


class NoseStatsd(Plugin):
    name = 'statsd'

    def options(self, parse, env=os.environ):
        super(NoseStatsd, self).options(parse, env=env)

    def configure(self, options, conf):
        super(NoseStatsd, self).configure(options, conf)

    def report(self, stream):
        def write(line):
            stream.writeln('%s' % line)

        if not hasattr(statsd, 'timings'):
            write("Statsd timings not saved, ensure your statsd client is: "
                  "STATSD_CLIENT = 'django_statsd.clients.nose'")
            return

        timings = {}
        longest = 0
        for v in statsd.timings:
            k = v[0].split('|')[0]
            longest = max(longest, len(k))
            timings.setdefault(k, [])
            timings[k].append(v[2])

        counts = {}
        for k, v in list(statsd.cache.items()):
            k = k.split('|')[0]
            longest = max(longest, len(k))
            counts.setdefault(k, [])
            [counts[k].append(_v) for _v in v]

        header = '%s | Number |  Avg (ms)  | Total (ms)' % (
            'Statsd Keys'.ljust(longest))
        header_len = len(header)

        write('')
        write('=' * header_len)
        write('%s | Number |  Avg (ms)  | Total (ms)' % (
            'Statsd Keys'.ljust(longest)))
        write('-' * header_len)
        if not timings:
            write('None')

        for k in sorted(timings.keys()):
            v = timings[k]
            write('%s | %s | %s | %s' % (
                k.ljust(longest),
                str(len(v)).rjust(6),
                ('%0.5f' % (sum(v) / float(len(v)))).rjust(10),
                ('%0.3f' % sum(v)).rjust(10)))

        write('=' * header_len)
        write('%s | Number | Total' % ('Statsd Counts'.ljust(longest)))
        write('-' * header_len)
        if not counts:
            write('None')

        for k in sorted(counts.keys()):
            v = counts[k]
            write('%s | %s | %d' % (
                k.ljust(longest),
                str(len(v)).rjust(6),
                sum([x * y for x, y in v])))
