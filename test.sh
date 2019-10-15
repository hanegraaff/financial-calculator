#!/bin/sh
coverage run --omit *venv*.py  run_tests.py
coverage report

