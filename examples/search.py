#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bluebird import BlueBird

query = {
    'fields': [
        {'items': ['brunn3is']},
    ]
}

for tweet in BlueBird().search(query, deep=True):
    print(tweet)