#!/usr/bin/env python3

from time import time
from sys import stdin, stdout, stderr
from os import environ
import os.path
from pathlib import Path


def download_files(files:list):
    outcomes = []
    print
    for f in files:
        filename_rel = os.path.join(*f)
        filename_abs = os.path.join(environ["TAL_META_DIR"], filename_rel)
        if os.path.exists(filename_abs):
            shutil.copy(filename_abs, environ["TAL_META_OUTPUT_FILES"])
            outcomes.append(f"File `{os.path.split(filename_rel)[-1]}` downloaded in the output folder.")
        else:
            outcomes.append(f"No problem-specific `{filename_rel}` getby file has been made available for this problem.")
    return outcomes

