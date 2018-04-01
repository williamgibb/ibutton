#!/usr/bin/env python
# -*- coding: utf-8 -*-
# XXX Update Docstring
"""
ibutton_gdd - button.py
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
import collections
# Third Party Code
# Custom Code
from ibutton.constants import *


log = logging.getLogger(__name__)

class ButtonData(object):
    def __init__(self):
        self.rows = []
        self.metadata = {}

    def check_integrity(self):
        rlen = len(self.rows)
        elen = int(self.metadata.get('Available mission samples'))
        if rlen != elen:
            raise ValueError('Missing available mission samples!, expected {} got {}'.format(rlen, elen))

    def append(self, row):
        self.rows.append(row)
