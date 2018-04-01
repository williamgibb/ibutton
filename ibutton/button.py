#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
ibutton_gdd - button.py
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

class ButtonData(object):
    def __init__(self):
        self.rows = []
        self.metadata = {}

    def check_integrity(self):
        if len(self.rows) != int(self.metadata.get('Total device samples')):
            raise ValueError('Missing samples!')

    def append(self, row):
        self.rows.append(row)