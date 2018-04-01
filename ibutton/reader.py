#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
ibutton_gdd - reader.py.py
Created on 4/1/18.


"""
# Stdlib
import os
import csv
import sys
import json
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

# 2015/12/22 00:01:00

def parse_order_csv(fp: str) -> dict:
    ret = {}
    with open(fp, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            ret[i] = row
    return ret

def parse_ibutton_csv(fp: str, order_d: dict):
    with open(fp, 'rb') as f:
        ibutton_found = False
        i = 0
        ibutton = button.ButtonData()
        ibutton.metadata[BLOCK] = order_d[i].get(BLOCK)
        ibutton.metadata[TMNT] = order_d[i].get(TMNT)
        lines = f.readlines()
        for line in lines:
            line = line.decode(encoding='latin-1').strip()

            if not line:
                if ibutton_found:
                    yield ibutton
                    i = i + 1
                    ibutton = button.ButtonData()
                    ibutton.metadata[BLOCK] = order_d[i].get(BLOCK)
                    ibutton.metadata[TMNT] = order_d[i].get(TMNT)
                    ibutton_found = False
                continue

            if 'download complete' in line:
                if ibutton.metadata != {} and ibutton.rows != []:
                    yield ibutton
                return

            key, value = line.split(',')

            key = key.strip('"')
            value = value.strip('"')
            if key.endswith(':'):
                key = key.rstrip(':')

            if key == 'Date/time logger downloaded':
                ibutton_found = True

            if ibutton_found:
                try:
                    key = datetime.datetime.strptime(key, TIME_FORMAT)
                except ValueError as e:
                    ibutton.metadata[key] = value
                else:
                    value = int(10*float(value))  # Convert units from celsius to decikelvins
                    ibutton.append((key, value))

            else:
                continue


# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)

    from pprint import pprint

    order_d = parse_order_csv(options.order)
    with s_cortex.openurl(options.core) as core:
        core.setConfOpts({'modules': (('ibutton.model.IButtonModel', {}),),
                          'caching': 1,
                          'cache:maxsize': 25000})
        with core.getCoreXact() as xact:
            fps = [options.input]
            if os.path.isdir(options.input):
                fps = [os.path.join(options.input, fn) for fn in os.listdir(options.input)]
            for fp in fps:
                log.info('Processing %s', fp)
                for i, button in enumerate(parse_ibutton_csv(fp, order_d)):
                    log.debug('Button # %s', i)
                    button.check_integrity()
                    # Make ibutton node
                    d = {SERIAL: button.metadata.get('Logger serial number'),
                         BLOCK: button.metadata.get(BLOCK),
                         TMNT: button.metadata.get(TMNT),
                         }
                    bnode = core.formTufoByProp('ibutton', d)
                    _, pprop = s_tufo.ndef(bnode)
                    if bnode[1].get('ibutton:serial') == "":
                        log.warning('Missing serial for ibutton!')
                    for k, v in button.rows:
                        # XXX TODO - timezone correction???
                        rtime = k.strftime(SYN_TIME_FORMAT)
                        d = {'button': pprop,
                             'rtime': rtime}
                        node = core.formTufoByProp('idata', d, temp=v)
                        if not node[1].get('.new'):
                            pass
                            # print('node existed!')
                            # print(node)
    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    # XXX Fill in description
    parser = argparse.ArgumentParser(description="Description.")
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, action='store',
                        help='Input file to process')
    parser.add_argument('-o', '--order_csv', dest='order', required=True, type=str,
                        action='store', help='Order CSV file')
    parser.add_argument('-c', '--core', dest='core', type=str, default='ram://',
                        action='store', help='Cortex to store data in')
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
