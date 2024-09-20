import os


def remove_readonly(func, path, excinfo=None):
    os.chmod(path, 0o777)
    func(path)
