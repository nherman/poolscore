#!/usr/bin/env python

import sys
import os
import shutil
import errno
import re
import subprocess
import argparse
from tempfile import mkstemp

basedir = os.path.dirname(os.path.abspath(__file__))
less_dir = os.path.join(basedir, "less")
poolscore_css_out = os.path.join(basedir, "poolscore/static/css")

def build_styles(args):
    env = {}
    for key in os.environ.keys():
        if key == 'PATH':
            env[key] = os.environ[key] + ":/usr/local/bin"
        else:
            env[key] = os.environ[key]
    lessc = ["lessc", 
        os.path.join(less_dir, "style.less"), 
        os.path.join(poolscore_css_out, "style.css"),
        "--verbose"]
    if args.compress:
        lessc.append("--compress")
    if args.lint:
        lessc.append("--lint")
    status = subprocess.call(lessc, env = env)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Less compiler wrapper.')
    parser.add_argument('-x','--compress', default = False, action = 'store_true', 
        help='Compresses output by removing some whitespaces. (Deprecated)', required = False)
    parser.add_argument('-l','--lint', default = False, action = 'store_true', 
        help='Syntax check only (lint).', required = False)
    args = parser.parse_args()
    build_styles(args)
