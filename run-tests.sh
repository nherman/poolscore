#!/bin/bash

export PS_ENV="Test"

python -m unittest poolscore.tests.test_auth
python -m unittest poolscore.tests.test_api