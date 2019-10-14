#!/bin/bash
rm dist/*
python setup.py install
python setup.py bdist_wheel
twine upload dist/*.whl

