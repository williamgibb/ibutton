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
        self.daily_minimums = {}
        self.daily_maximums = {}
        self.daily_average = {}
        self.missing_full_days = set([])
        self.daily_halfday_average = {}
        self.missing_half_days = set([])
        self.gdd = {}  # Year -> count

    def check_integrity(self):
        rlen = len(self.rows)
        elen = int(self.metadata.get('Available mission samples'))
        if rlen != elen:
            raise ValueError('Missing available mission samples!, expected {} got {}'.format(rlen, elen))

    def append(self, row):
        self.rows.append(row)

    def analyze_button(self):
        # Compute whole day data
        self.compute_daily_data()
        # Compute half day data
        self.compute_half_day_data()
        # Compute growing days
        self.compute_gdd()

    def compute_daily_data(self):
        daily_data = collections.defaultdict(list)
        max_len = 0
        for dt, temp in self.rows:
            day = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
            daily_data[day].append(temp)
        for day, temps in daily_data.items():
            l = len(temps)
            if l > max_len:
                max_len = l

        if max_len == 0:
            raise ValueError('No temps data available')

        for day in sorted(list(daily_data.keys())):
            temps = daily_data.get(day)
            if len(temps) < max_len:
                log.debug('Day {} is missing samples - expected {}, got {}.'.format(day, max_len, len(temps)))
                self.missing_full_days.add(day)
                continue
            # log.info('{} - # of samples {}'.format(day, len(temps)))
            s = sum(temps)
            avg_temp = s / len(temps)
            min_temp = min(temps)
            max_temp = max(temps)
            self.daily_minimums[day] = min_temp
            self.daily_maximums[day] = max_temp
            self.daily_average[day] = avg_temp

    def compute_half_day_data(self):
        daily_data = collections.defaultdict(list)
        max_len = 0
        for dt, temp in self.rows:
            # Ensure we're collecting samples between 7am and 7pm
            if dt.hour < 7 or dt.hour > 18:
                continue
            day = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
            daily_data[day].append(temp)

        for day, temps in daily_data.items():
            l = len(temps)
            if l > max_len:
                max_len = l

        if max_len == 0:
            raise ValueError('No temps data availible')
        if max_len != 24:
            log.debug('Expected to get 24 samples in a half day period; only got {}'.format(max_len))

        for day in sorted(list(daily_data.keys())):
            temps = daily_data.get(day)
            if len(temps) < max_len:
                log.debug('Half day {} is missing samples - expected {}, got {}.'.format(day, max_len, len(temps)))
                self.missing_half_days.add(day)
                continue
            s = sum(temps)
            avg_temp = s / len(temps)
            self.daily_halfday_average[day] = avg_temp

    def compute_gdd(self):
        if not self.daily_minimums:
            raise ValueError('Must compute daily minimums first')
        if not self.daily_maximums:
            raise ValueError('Must compute daily maximums first.')
        dmindays = set(list(self.daily_minimums.keys()))
        dmaxdays = set(list(self.daily_maximums.keys()))
        if dmindays != dmaxdays:
            raise ValueError('Missing days between daily min and max values.')

        log.debug('Computing GDD between: {} and {}'.format(min(dmindays), max(dmindays)))

        # GDD = true if [ (daily min + daily max)/2 ] - 10 deg C
        # Yes, 10C is a baseline temperature for metabolic activity in grapes.
        # A presumed ave daily temperature would have a GDD of 0. Any daily average temp > 10C would indicate GDD.
        dmindays = list(dmindays)
        dmindays.sort()
        current_year = dmindays[0].year
        log.debug('Starting with gdd for [{}]'.format(current_year))
        for day in dmindays:
            if day.year > current_year:
                log.debug('Now computing gdd for [{}]'.format(current_year))
                current_year = day.year
            avg_temp = (self.daily_minimums.get(day) + self.daily_maximums.get(day)) / 2
            if avg_temp > 10:  # XXX What about >= ????
                if current_year in self.gdd:
                    self.gdd[current_year] = self.gdd[current_year] + 1
                else:
                    self.gdd[current_year] = 1

    def write_computed_data_to_files(self, fdir=None):
        if not fdir:
            fdir = os.getcwd()

        tmnt, block = self.metadata.get(TMNT), self.metadata.get(BLOCK)

        fn_base = 'block_{}_tmnt_{}'.format(block, tmnt)
        fn = '{}_gdd.csv'.format(fn_base)
        fp = os.path.join(fdir, fn)
        with open(fp, 'w') as f:
            w = csv.DictWriter(f, [TMNT, BLOCK, 'year', 'gdd'])
            w.writeheader()
            for k, v in self.gdd.items():
                d = {'year': k,
                     'gdd': v,
                     TMNT: tmnt,
                     BLOCK: block}
                w.writerow(d)
        fn = '{}_daily_min.csv'.format(fn_base)
        fp = os.path.join(fdir, fn)
        with open(fp, 'w') as f:
            w = csv.DictWriter(f, [TMNT, BLOCK, 'date', 'daily_min'])
            w.writeheader()
            for k, v in self.daily_minimums.items():
                d = {
                    'date': k,
                    'daily_min': v,
                    TMNT: tmnt,
                    BLOCK: block
                    }
                w.writerow(d)
        fn = '{}_daily_max.csv'.format(fn_base)
        fp = os.path.join(fdir, fn)
        with open(fp, 'w') as f:
            w = csv.DictWriter(f, [TMNT, BLOCK, 'date', 'daily_max'])
            w.writeheader()
            for k, v in self.daily_maximums.items():
                d = {
                    'date': k,
                    'daily_max': v,
                    TMNT: tmnt,
                    BLOCK: block
                }
                w.writerow(d)
        fn = '{}_daily_avg.csv'.format(fn_base)
        fp = os.path.join(fdir, fn)
        with open(fp, 'w') as f:
            w = csv.DictWriter(f, [TMNT, BLOCK, 'date', 'daily_avg'])
            w.writeheader()
            for k, v in self.daily_average.items():
                d = {
                    'date': k,
                    'daily_avg': v,
                    TMNT: tmnt,
                    BLOCK: block
                }
                w.writerow(d)
        fn = '{}_daily_midday_avg.csv'.format(fn_base)
        fp = os.path.join(fdir, fn)
        with open(fp, 'w') as f:
            w = csv.DictWriter(f, [TMNT, BLOCK, 'date', 'midday_avg'])
            w.writeheader()
            for k, v in self.daily_halfday_average.items():
                d = {
                    'date': k,
                    'midday_avg': v,
                    TMNT: tmnt,
                    BLOCK: block
                }
                w.writerow(d)
