#!/usr/bin/python

"""raspi_config.py"""

import argparse
import os
import subprocess
from constants import *


def parse_args():
    """Initialize argument parser.

    Returns:
        An instance of argparse.Argument parser.
    """

    parser = argparse.ArgumentParser()
    
    # Add arguments
    # Path to the image file, it is optional because it will give the option
    # to download the image.
    parser.add_argument("-img", "--image", help="path to the raspbian image")

    return parser.parse_args()


def create_folder(path):
    """Create a simple folder

    Args:
        path: The path of the folder.

    Returns:
        The exit status of the command.
    """

    return subprocess.run(["mkdir", "-p", path]).returncode


def prepare(img_path):
    """Create folder and mount image.

    Args:
        img_path: Path to the image file.
    """

    # Create folders
    status = create_folder(boot_path)
    if status:
        raise RuntimeError("Creation of boot folder failed"
                           " with exit status {}".format(status))

    status = create_folder(root_path)
    if status:
        raise RuntimeError("Creation of root folder failed"
                           " with exit status {}".format(status))


def clean_up():
    """Clean up folders."""
    return subprocess.run(["rm", "-rf", tmp_path])


if __name__ == "__main__":
    """Main programm"""

    args = parse_args()

    prepare()

    # Clean up
    status = clean_up()
    if not status:
        raise RuntimeError("Rm failed with exit status {}".format(status))
