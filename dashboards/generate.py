#!/usr/bin/env python3
"""
Generates Grafana dashboard files for PowerDNS server statistics in the
current directory.
"""

import os
import sys
import json
import copy
import string


# Where to output the files
DIR = os.path.abspath(os.path.dirname(__file__))

DATASOURCE = "metronome"


class Dashboard:
    
    def __init__(self, title):
        self.data = {
            "___NOTE___": "AUTOMATICALLY GENERATED by dashboards/generate.py",
            "id": None,
            "title": title,
            "tags": [],
            "style": "light",
            "timezone": "browser",
            "editable": True,
            "hideControls": False,
            "sharedCrosshair": True,
            "rows": [],
            "time": {
                "from": "now-6h",
                "to": "now"
            },
            "timepicker": {
                "refresh_intervals": [
                    "5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"
                ],
                "time_options": [
                    "5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"
                ]
            },
            "templating": {
                "list": []
            },
            "annotations": {
                "list": []
            },
            "refresh": False,
            "schemaVersion": 12,
            "version": 9,
            "links": [],
            "gnetId": None
        }
        self.last_id = 0

    def add_template_var(self, name, label, query, regex="", multi=False, include_all=False):
        self.data['templating']['list'].append({
            "current": {},
            "datasource": DATASOURCE,
            "hide": 0,
            "includeAll": include_all,
            "label": label,
            "multi": multi,
            "name": name,
            "options": [],
            "query": query,
            "refresh": 1,
            "regex": regex,
            "type": "query"
        })

    def add_graph_row(self, title, targets, collapse=False, stack=False, 
                      y_min=0, y_max=None, y_format='short'):
        assert isinstance(targets, list)
        panel = {
           "title": title,
           "datasource": DATASOURCE,
           "aliasColors": {},
           "bars": False,
           "editable": True,
           "error": False,
           "fill": 1,
           "grid": {
             "threshold1": None,
             "threshold1Color": "rgba(216, 200, 27, 0.27)",
             "threshold2": None,
             "threshold2Color": "rgba(234, 112, 112, 0.22)"
           },
           "id": self._next_id(),
           "isNew": True,
           "legend": {
             "avg": False,
             "current": False,
             "max": False,
             "min": False,
             "show": True,
             "total": False,
             "values": False
           },
           "lines": True,
           "linewidth": 2,
           "links": [],
           #"nullPointMode": "connected",
           "nullPointMode": "null",
           "percentage": False,
           "pointradius": 5,
           "points": False,
           "renderer": "flot",
           "seriesOverrides": [],
           "span": 12,
           "stack": stack,
           "steppedLine": False,
           "targets": [
             { "hide": False, "refId": string.ascii_uppercase[i], "target": x } 
             for i, x in enumerate(targets)
           ],
           "timeFrom": None,
           "timeShift": None,
           "tooltip": {
             "msResolution": True,
             "shared": True,
             "sort": 0,
             "value_type": "cumulative"
           },
           "type": "graph",
           "xaxis": {
             "show": True
           },
           "yaxes": [
             {
               "format": y_format,
               "label": None,
               "logBase": 1,
               "max": y_max,
               "min": y_min,
               "show": True
             },
             {
               "format": "short",
               "label": None,
               "logBase": 1,
               "max": None,
               "min": None,
               "show": True
             }
           ]
        }
        row = {
            "title": title,
            "collapse": collapse,
            "editable": True,
            "height": "250px",
            "panels": [panel],
        }
        self.data['rows'].append(row)
    
    def save(self, fpath):
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(
                self.data, f, indent=2, ensure_ascii=False, sort_keys=True)

    def _next_id(self):
        self.last_id += 1
        return self.last_id


dnsdist = Dashboard(title="PowerDNS dnsdist [default]")
dnsdist.add_template_var(
    name='dnsdist', label='dnsdist server', query='dnsdist.*', multi=False)

dnsdist.add_graph_row(
    title='Number of queries',
    targets=[
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.servfail-responses), 10), 'Servfail/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.queries), 10), 'Queries/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.responses), 10), 'Responses/s')",
    ],
)

dnsdist.add_graph_row(
    title='Latency (answers/s in a latency band)',
    targets=[
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.latency0-1), 10), '<1 ms')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.latency1-10), 10), '<10 ms')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.latency10-50), 10), '<50 ms')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.latency50-100), 10), '<100 ms')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.latency100-1000), 10), '<1000 ms')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.latency-slow), 10), 'With slow answers')",
    ],
    stack=True
)

dnsdist.add_graph_row(
    title='Timeouts and errors',
    targets=[
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.downstream-timeouts), 10), 'Timeouts/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.downstream-send-errors), 10), 'Errors/s')",
    ],
)

dnsdist.add_graph_row(
    title='Query drops',
    targets=[
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.rule-drop), 10), 'Rule drops/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.acl-drops), 10), 'ACL drops/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.dyn-blocked), 10), 'Dynamic drops/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.block-filter), 10), 'Blockfilter drops/s')",
    ],
)


def compact(s):
    return ' '.join( x.strip() for x in s.split('\n') ).strip()

# TODO: filter out small values? Now a single miss will show as 100%
dnsdist.add_graph_row(
    title='Cache miss rate',
    y_format='percentunit',
    targets=[
        compact("""
        alias(movingAverage(
            divideSeries(
                perSecond(dnsdist.$dnsdist.main.cache-misses),
                sumSeries(
                    perSecond(dnsdist.$dnsdist.main.cache-misses), 
                    perSecond(dnsdist.$dnsdist.main.cache-hits)
                )
            )
        , 10), 'cache miss rate (%)')
        """)
    ],
)

dnsdist.add_graph_row(
    title='Query policy',
    targets=[
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.rdqueries), 10), 'RD Queries/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.rule-nxdomain), 10), 'Rule NXDomain/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.self-answered), 10), 'Rule self-answered/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.no-policy), 10), 'Rule self-answered/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.noncompliant-queries), 10), 'Non-compliant queries/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.noncompliant-responses), 10), 'Non-compliant responses/s')",
        "alias(movingAverage(perSecond(dnsdist.$dnsdist.main.empty-queries), 10), 'Empty queries/s')",
    ],
)

dnsdist.add_graph_row(
    title='Average latency',
    y_format='µs',
    targets=[
        "alias(dnsdist.$dnsdist.main.latency-avg100, '100 packet average')",
        "alias(dnsdist.$dnsdist.main.latency-avg10000, '10,000 packet average')",
        "alias(dnsdist.$dnsdist.main.latency-avg1000000, '1,000,000 packet average')",
    ],
)

dnsdist.add_graph_row(
    title='CPU usage',
    y_format='percent',
    stack=True,
    targets=[
        "alias(scale(movingAverage(perSecond(dnsdist.$dnsdist.main.cpu-sys-msec), 10), 0.1), 'System CPU')",
        "alias(scale(movingAverage(perSecond(dnsdist.$dnsdist.main.cpu-user-msec), 10), 0.1), 'Total (system+user) CPU')",
    ],
)

dnsdist.add_graph_row(
    title='Memory usage',
    y_format='bytes',
    targets=[
        "alias(dnsdist.$dnsdist.main.real-memory-usage, 'Memory usage')",
    ],
)

dnsdist.add_graph_row(
    title='File descriptor usage',
    targets=[
        "alias(dnsdist.$dnsdist.main.fd-usage, 'Number of file descriptors')",
    ],
)

dnsdist.add_graph_row(
    title='Uptime',
    y_format='s',
    targets=[
        "alias(dnsdist.$dnsdist.main.uptime, 'Uptime')",
    ],
)

dnsdist.add_graph_row(
    title='Dynamic block size',
    collapse=True,
    targets=[
        "alias(dnsdist.$dnsdist.main.dyn-block-nmg-size, 'Number of entries')",
    ],
)

dnsdist.add_graph_row(
    title='Queries/s per server',
    targets=[
        "aliasByNode(movingAverage(perSecond(dnsdist.$dnsdist.main.servers.*.queries), 10), 4)",
    ],
)
dnsdist.add_graph_row(
    title='Drops/s per server',
    targets=[
        "aliasByNode(movingAverage(perSecond(dnsdist.$dnsdist.main.servers.*.drops), 10), 4)",
    ],
)
dnsdist.add_graph_row(
    title='Send errors/s per server',
    targets=[
        "aliasByNode(movingAverage(perSecond(dnsdist.$dnsdist.main.servers.*.senderrors), 10), 4)",
    ],
)
dnsdist.add_graph_row(
    title='Latency per server',
    y_format='µs',
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.servers.*.latency, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Outstanding per server',
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.servers.*.outstanding, 4)",
    ],
)

dnsdist.add_graph_row(
    # TODO: test this one
    title='Queries/s per frontend',
    collapse=True,
    targets=[
        "aliasByNode(movingAverage(perSecond(dnsdist.$dnsdist.main.frontends.*.queries), 10), 4)",
    ],
)

dnsdist.add_graph_row(
    title='Servers per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.servers, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache size per pool (max number of entries)',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-size, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache size per pool (current number of entries)',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-entries, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache hits per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-hits, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache misses per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-misses, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache deferred inserts per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-deferred-inserts, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache deferred lookups per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-deferred-lookups, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache lookup collisions per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-lookup-collisions, 4)",
    ],
)
dnsdist.add_graph_row(
    title='Cache insert collisions per pool',
    collapse=True,
    targets=[
        "aliasByNode(dnsdist.$dnsdist.main.pools.*.cache-insert-collisions, 4)",
    ],
)



dnsdist.save(os.path.join(DIR, 'dnsdist.json'))

