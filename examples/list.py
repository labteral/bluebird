#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bluebird import BlueBird


for user in BlueBird().get_list_members('dalvarez37', 'xiii-legislatura-congreso'):
    print(user)