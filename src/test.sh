#!/bin/sh
coverage run --omit *venv*.py,*test/*,*__init__* run_tests.py
coverage report
