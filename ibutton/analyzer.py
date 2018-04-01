#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
ibutton_gdd - analyzer.py
Created on 4/1/18.


"""
# Stdlib
import argparse
import json
import logging
import os
import sys

# Third Party Code
# Custom Code


log = logging.getLogger(__name__)


# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)

    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    # XXX Fill in description
    parser = argparse.ArgumentParser(description="Description.")
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, action='store',
                        help='Input file to process')
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
