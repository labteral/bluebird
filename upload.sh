#!/bin/bash
rm dist/*
python3 setup.py install
python3 setup.py bdist_wheel
twine upload dist/*.whl

