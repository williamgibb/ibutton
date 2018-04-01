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
# Custom Code


log = logging.getLogger(__name__)

# 2015/12/22 00:01:00
TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
SYN_TIME_FORMAT = '%Y%m%d%H%M%S'
BLOCK = 'block'
TMNT = 'tmnt'
LOCATION_KEYS = [BLOCK, TMNT]

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
        ibutton = ButtonData()
        ibutton.metadata[BLOCK] = order_d[i].get(BLOCK)
        ibutton.metadata[TMNT] = order_d[i].get(TMNT)
        lines = f.readlines()
        for line in lines:
            line = line.decode(encoding='latin-1').strip()

            if not line:
                if ibutton_found:
                    yield ibutton
                    i = i + 1
                    ibutton = ButtonData()
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
                    value = float(value)
                    ibutton.append((key, value))

            else:
                continue
                # print(key, value)


# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)

    from pprint import pprint

    order_d = parse_order_csv(options.order)
    pprint(order_d)
    for button in parse_ibutton_csv(options.input, order_d):
        pprint((button, len(button.rows), button.metadata))
        pass

    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    # XXX Fill in description
    parser = argparse.ArgumentParser(description="Description.")
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, action='store',
                        help='Input file to process')
    parser.add_argument('-o', '--order_csv', dest='order', required=True, type=str,
                        action='store', help='Order CSV file')
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
