import os.path
import sys


def get_screenshots_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    screenshots_dir = os.path.join(base, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    return screenshots_dir