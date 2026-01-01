def read_file(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return data