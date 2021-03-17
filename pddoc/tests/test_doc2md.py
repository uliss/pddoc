#!/usr/bin/env python
# coding=utf-8

__author__ = 'Serge Poltavski'

import unittest
import os
import subprocess
from .nologging import *

BIN_PATH = os.path.join(os.path.dirname(__file__), "..", "bin", "pd_doc2md.py")

SAMPLE_PDDOC = "complex.pddoc"
SAMPLE_MD = "out/complex.md"


def clean():
    try:
        # os.remove("image.png")
        os.remove(SAMPLE_MD)
    except OSError:
        pass


class TestDoc2Markdown(unittest.TestCase):
    def setUp(self):
        clean()

    def tearDown(self):
        pass

    def test_run_simple(self):
        nolog = NoLogging()
        rc = subprocess.call(["python", BIN_PATH, "not-exists"])
        self.assertNotEqual(rc, 0)

        rc = subprocess.call(["python", BIN_PATH, SAMPLE_PDDOC, SAMPLE_MD])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(SAMPLE_MD))  # default output name
