#!/usr/bin/env python
# -*- coding: utf-8 -*-

from polypus import TwitterScraper


for user in TwitterScraper().get_list_members('dalvarez37', 'xiii-legislatura-congreso'):
    print(user)