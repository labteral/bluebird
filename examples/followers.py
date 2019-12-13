#!/usr/bin/env python
# -*- coding: utf-8 -*-

from polypus import TwitterScraper


for username in TwitterScraper().get_followers('brunn3is'):
    print(username)