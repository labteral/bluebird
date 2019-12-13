#!/usr/bin/env python
# -*- coding: utf-8 -*-

from polypus import TwitterScraper

query = {
    'fields': [
        {'items': ['brunn3is']},
    ]
}

for tweet in TwitterScraper().search(query, deep=True):
    print(tweet)