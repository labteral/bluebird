#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bluebird import BlueBird

for username in BlueBird().get_followers('brunn3is'):
    print(username)