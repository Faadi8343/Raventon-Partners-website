"""Vercel serverless entry point: every /api/* request is rewritten here (see vercel.json)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _core import VercelHandler  # noqa: E402


class handler(VercelHandler):
    pass
