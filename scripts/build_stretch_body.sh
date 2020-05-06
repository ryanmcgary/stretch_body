#! /bin/bash
cd ../python
rm -rf dist
rm -rf build
rm -rf *.egg-info
python setup.py sdist bdist_wheel
python -m twine upload dist/*
#echo 'Uploaded stretch_body to Pypi'
