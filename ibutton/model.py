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
        def warn(evt):
            oldv, newv = evt[1].get('oldv'), evt[1].get('newv')
            prop = evt[1].get('prop')
            if oldv:
                log.warning('Smashing %s with %s vs %s', prop, newv, oldv)

        self.core.on('node:prop:set', warn, form='idata')

    @staticmethod
    def getBaseModels():

        modl = {
            'types': (
                ('ibutton', {'subof': 'comp', 'fields': 'serial=str:lwr,block=int,tmnt=str:lwr',
                             'doc': 'A unique ibutton'}),
                ('idata', {'subof': 'comp', 'fields': 'button=ibutton,rtime=time',
                           'doc': 'A datapoint for an ibutton in time'}),
            ),

            'forms': (
                ('idata', {}, (
                    ('rtime', {'ptype': 'time', 'req': 1, 'ro': 1, 'doc': 'Time of the databpoint'}),
                    ('button', {'ptype': 'ibutton'}),
                    ('temp', {'ptype': 'int', 'doc': 'Temperature (in deciCelsius)'}),

                )),
                ('ibutton', {}, (
                    ('serial', {'ptype': 'str:lwr', 'ro': 1, 'req': 1, 'doc': 'ibutton serial number'}),
                    ('block', {'ptype': 'int', 'ro': 1, 'req': 1, 'doc': 'ibutton block number'}),
                    ('tmnt', {'ptype': 'str:lwr', 'ro': 1, 'req': 1, 'doc': 'trearment for the ibutton'}),
                ))
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
