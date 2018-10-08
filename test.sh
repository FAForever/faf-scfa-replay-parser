#!/usr/bin/env bash

pyclean .

PATH=$PATH:. python3.6 -m pytest -s --cov=replay_parser -rxs `find ./tests/conftest.py ./tests/fixtures/ ./tests/unittests/ -iname "*.py"`
