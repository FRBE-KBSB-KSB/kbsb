from pathlib import Path

import toml


def read_version():
    with open("pyproject.toml") as f:
        mt = toml.load(f)
        return mt["project"]["version"]


version = read_version()

ROOT_DIR = (Path(__file__).parents[2]).resolve()
