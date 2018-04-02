#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
ibutton_gdd - analyzer.py
Created on 4/1/18.


"""
# Stdlib
import os
import csv
import sys
import logging
import argparse
import datetime

# Third Party Code
import synapse.cortex as s_cortex

import synapse.lib.tufo as s_tufo

# Custom Code
import ibutton.button as button
from ibutton.constants import *

log = logging.getLogger(__name__)

def analyze(core, fdir):
    d = {}
    for inode in core.eval('ibutton'):
        _, pprop = s_tufo.ndef(inode)
        log.info('Collecting data for {}'.format(pprop))
        ibutton = button.ButtonData()
        props = s_tufo.props(inode)
        ibutton.metadata[TMNT] = props.get(TMNT)
        ibutton.metadata[BLOCK] = props.get(BLOCK)
        for node in core.eval('idata:button=%s' % pprop):
            props = s_tufo.props(node)
            tick = props.get('rtime')
            # Taken from synapse.lib.time
            dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=tick)
            # from dC (int) to C (float)
            v = float(props.get('temp')) / 10
            ibutton.append((dt, v))
        d[pprop] = ibutton

    summer_rows = []
    for pprop, ibutton in d.items():
        log.info('Analyzing data for {}'.format(pprop))
        ibutton.analyze_button()
        ibutton.write_computed_data_to_files(fdir)
        for k, v in ibutton.summer_gdd.items():
            d = {'year': k,
                 'gdd': v,
                 TMNT: ibutton.metadata.get(TMNT),
                 BLOCK: ibutton.metadata.get(BLOCK)}
            summer_rows.append(d)

    fn = 'aggregate_summer_gdd.csv'
    fp = os.path.join(fdir, fn)
    with open(fp, 'w') as f:
        w = csv.DictWriter(f, [TMNT, BLOCK, 'year', 'gdd'])
        w.writeheader()
        for d in summer_rows:
            w.writerow(d)
    total_summer_gdd = sum([d.get('gdd') for d in summer_rows])
    log.info('Total summer gdd rows: [%s] [%s]', total_summer_gdd, (total_summer_gdd/len(summer_rows)))

# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)

    if not os.path.exists(options.output):
        os.makedirs(options.output)

    with s_cortex.openurl(options.core) as core:
        core.setConfOpts({'modules': (('ibutton.model.IButtonModel', {}),),
                          'caching': 1,
                          'cache:maxsize': 25000})
        with core.getCoreXact() as xact:
            analyze(core, options.output)

    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    # XXX Fill in description
    parser = argparse.ArgumentParser(description="Description.")
    parser.add_argument('-o', '--output', dest='output', required=True, type=str, action='store',
                        help='Directory to write data too')
    parser.add_argument('-c', '--core', dest='core', type=str, required=True,
                        action='store', help='Cortex with data in it')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                        help='Enable verbose output')
    return parser


def _main():  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(funcName)s]')
    p = makeargpaser()
    opts = p.parse_args()
    main(opts)


if __name__ == '__main__':  # pragma: no cover
    _main()
