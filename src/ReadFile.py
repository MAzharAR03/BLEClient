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

def resource_path(relative_path):
    """ Get path to resource working for both IDE and adjacent files next to the .exe """
    if getattr(sys, 'frozen', False):
        # We are running as a compiled .exe
        # sys.executable is the exact path to Server.exe
        base_path = os.path.dirname(sys.executable)
    else:
        # We are running in the IDE
        # __file__ is the exact path to this python script
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)