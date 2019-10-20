#!/bin/sh
coverage run --omit *venv*.py,*test/test* run_tests.py
coverage report

