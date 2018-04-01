#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
ibutton_gdd - model.py.py
Created on 4/1/18.


"""
# Stdlib
import argparse
import json
import logging
import os
import sys

# Third Party Code
import synapse.cortex as s_cortex
import synapse.lib.module as s_module
# Custom Code


log = logging.getLogger(__name__)



class IButtonModel(s_module.CoreModule):

    def postCoreModule(self):
        pass
        # XXX Add node:prop:set handler to identify :temp values being
        # smashed so we know if something got whacky

    @staticmethod
    def getBaseModels():

        modl = {
            'types': (
                ('datapoint', {'subof': 'comp', 'fields': 'row=int,block=int,rtime=time'}),
                ('ibutton', {'subof': 'str', 'lower': 1, 'doc': 'A unique ibutton'})
            ),

            'forms': (
                ('datapoint', {}, (
                    ('row', {'ptype': 'int', 'req': 1, 'ro': 1, 'doc': 'Row location of the databpoint'}),
                    ('block', {'ptype': 'int', 'req': 1, 'ro': 1, 'doc': 'Block location of the databpoint'}),
                    ('rtime', {'ptype': 'time', 'req': 1, 'ro': 1, 'doc': 'Time of the databpoint'}),
                    ('temp', {'ptype': 'int', 'doc': 'Temparture (in decikelvin)'}),
                    ('button', {'ptype': 'ibutton'})
                )),
            ),

        }
        return (('ibutton', modl),)


# noinspection PyMissingOrEmptyDocstring
def main(options):  # pragma: no cover
    if not options.verbose:
        logging.disable(logging.DEBUG)

    core = s_cortex.openurl('ram://')
    core.setConfOpt('modules', (('ibutton.model.IButtonModel', {}),))
    assert 'ibutton.model.IButtonModel' in core.getCoreMods()

    sys.exit(0)


# noinspection PyMissingOrEmptyDocstring
def makeargpaser():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Description.")
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
