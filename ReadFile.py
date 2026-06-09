import os
import sys

def read_file_b(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_path, filename)

    with open(file_path, "rb") as f:
        data = f.read()
    return data

def read_file(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(base_path, filename)

    with open(file_path, "r") as f:
        data = f.read()
    return data