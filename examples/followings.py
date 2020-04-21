#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bluebird import BlueBird


for username in BlueBird().get_followings('brunn3is'):
    print(username)