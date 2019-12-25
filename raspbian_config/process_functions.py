"""process_functions.py"""

import argparse
import os
import subprocess
from questions import *
from constants import *


def create_folder(path):
    """Create a simple folder

    Args:
        path: The path of the folder.

    Returns:
        The exit status of the command.
    """

    return subprocess.run(["mkdir", "-p", path]).returncode


def process_fdisk_output(img_path):
    """Process fdisk output to get loop offsets for mounting partitions.

    Args:
        img_path: The path of the img file.

    Returns:
        A tuple of type (boot_offset, root_offset)
    """

    fdisk_output = subprocess.check_output(["fdisk", "-l", img_path])
    fdisk_lines = fdisk_output.splitlines()
    fdisk_lines = [line.decode("utf-8") for line in fdisk_lines]

    for line in fdisk_lines:
        start = line.split(" ")[0]
        # Sector size
        if start == "Units:":
            sector_size = int(line.split("=")[-1].split("bytes")[0])
        # Start of boot partition
        elif start == (img_path.split('/')[-1] + "1"):
            for el in line.split(" ")[1:]:
                if el != "":
                    boot_start = int(el)
                    break
        # Start of root partition
        elif start == (img_path.split('/')[-1] + "2"):
            for el in line.split(" ")[1:]:
                if el != "":
                    root_start = int(el)
                    break

    boot_offset = sector_size * boot_start
    root_offset = sector_size * root_start

    return boot_offset, root_offset


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


def mount_partition(img_path, target_path, offset):
    """Mount a raspberry partition to a specific folder.

    Args:
        img_path: The path of image file.
        target_path: The folder where the partition will be mounted.
        offset: The loopback offset.

    Returns:
        Status code of command.
    """

    status = subprocess.run(["sudo", "mount", "-o", "loop,offset="+str(offset),
                             img_path, target_path])

    return status


def unmount(target_path):
    """Unmount a partition.

    Args:
        target_path: The folder where the partition is mounted.

    Returns:
        Status code of command.
    """

    status = subprocess.run(["sudo", "umount", target_path])
    return status


def clean_up():
    """Clean up folders."""

    return subprocess.run(["rm", "-rf", tmp_path])


def yes_no_question(attribute, message):
    """Make a question about a feauture

    Args:
        attribute (str): The feature to be implemented.
        message (str): The question to ask.

    Return:
        O for N 1 for Y
    """

    questions = [
        {
            'type': 'confirm',
            'name': attribute,
            'message': message,
            'default': True
        }
    ]
    answers = prompt(questions)
   
    return answers[attribute]


def get_input(attribute, message):
    """Ask user for input"""

    questions = [
        {
            'type': 'input',
            'name': attribute,
            'message': message,
        }
    ]
    answers = prompt(questions)

    return answers[attribute]


def enable_ssh():
    """Enable ssh on first boot."""
    
    subprocess.run(["sudo", "touch", boot_path + "/ssh"])


def add_ssid_psk(ssid, psk):
    """Add ssid and psk entry to /etc/wpa_supplicant/wpa_supplicant.conf file.

    Args:
        ssid: The ssid of wifi network.
        psk: The password of the wifi network.
    """
    
    new_network = \
        "\\\n\\\nnetwork={{\\\n\\\tssid={}\\\n\\\tpsk={}\\\n}}".format(ssid, psk)

    conf_path = root_path + "/etc/wpa_supplicant/wpa_supplicant.conf"
    subprocess.run(["sudo", "sed", "-i", "-e",
                    '$ a {}'.format(new_network), conf_path])


def enable_avahi():
    """Enable publish workstation in avahi daemon config file."""

    conf_path = root_path + "/etc/avahi/avahi-daemon.conf"
    subprocess.run(["sudo", "sed", "-i", 
                    "s/publish-workstation=no/publish-workstation=yes/",
                    conf_path])


def change_hostname(hostname):
    """Change hostname for the pi.

    It modifies the /etc/hosts and /etc/hostname files.

    Args:
        hostname: The new hostname
    """

    conf_path = root_path + "/etc/hostname"

    # get old hostname
    old_host = subprocess.check_output(["cat", conf_path]).decode("utf-8")
    old_host = old_host.strip("\n")

    subprocess.run(["sudo", "sed", "-i",
                    "s/{}/{}/".format(old_host, hostname), conf_path])

    conf_path = root_path + "/etc/hosts"
    subprocess.run(["sudo", "sed", "-i",
                    "s/{}/{}/".format(old_host, hostname), conf_path])
