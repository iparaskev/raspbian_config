"""__init__.py"""

import argparse
import os
from .process_functions import *
from .constants import *
from .questions import *


def parse_args():
    """Initialize argument parser.

    Returns:
        An instance of argparse.Argument parser.
    """

    parser = argparse.ArgumentParser()

    # Add arguments
    # Path to the image file, it is optional because it will give the option
    # to download the image.
    parser.add_argument("img", help="path to the raspbian image")
    parser.add_argument("-i", "--interactive", help="use interactive option,"
                                                    " if this option is in use"
                                                    " the individual args are"
                                                    " skipped",
                        action="store_true")
    parser.add_argument("--ssh", help="enable ssh", action="store_true")
    parser.add_argument("--avahi", help="enable avahi daemon",
                        action="store_true")
    parser.add_argument("--ssid", help="ssid of local network",
                        type=str, default="")
    parser.add_argument("--psk", help="password of local network",
                        type=str, default="")
    parser.add_argument("--hostname", help="change hostname",
                        type=str, default="")

    return parser.parse_args()


def choose(int_flag, func, f_args, cli_arg):
    """Choose from the cli argument or the interactive flag

    Args:
        int_flag (bool): A flag indicating interactive input from user or not.
        func (function): The question function.
        f_args (dict): The arguments of the function.
        cli_arg (): Variable from argparse.

    Returns:
        (any): The return value.
    """
    ret = func(*f_args) if int_flag else cli_arg
    return ret


def main():
    """Main programm"""

    args = parse_args()

    # Prepare folders
    prepare(args.img)

    # Get offsets of partitions.
    boot_offset, root_offset = process_fdisk_output(args.img)

    # Ask for ssh
    status = choose(args.interactive, yes_no_question,
                    ["ssh", "Do you want to enable ssh?"], args.ssh)
    if status:
        # Mount boot partition
        mount_partition(args.img, boot_path, boot_offset)

        # Create ssh file
        enable_ssh()

        # Unmount boot partition
        unmount(boot_path)

    # Add wifi
    ssid = None
    psk = None
    wf_status = choose(args.interactive, yes_no_question,
                       ["wifi", "Connect to local wifi?"],
                       bool(args.psk or args.ssid))  # bool("") = False
    if wf_status:
        ssid = choose(args.interactive, get_input,
                      ["ssid", "Type ssid of wifi:"], args.ssid)
        psk = choose(args.interactive, get_input,
                     ["psk", "Type password of wifi:"], args.psk)

    # Change hostname
    host_status = choose(args.interactive, yes_no_question,
                         ["hostname", "Change hostname?"],
                         bool(args.hostname))
    if host_status:
        hostname = choose(args.interactive, get_input,
                          ["hostname", "Type new hostname:"], args.hostname)

    # Enable avahi daemon
    avahi_status = choose(args.interactive, yes_no_question,
                          ["avahi", "Enable avahi daemon?"],
                          bool(args.avahi))

    # Or the binary options
    mount_status = (wf_status | avahi_status | host_status)

    # If it needs to mount rootfs
    if mount_status:
        # Mount boot partition
        mount_partition(args.img, root_path, root_offset)

        # Check for wifi
        if wf_status:
            add_ssid_psk(ssid, psk)

        # Change hostname
        if host_status:
            change_hostname(hostname)

        # Enable publish workstation of avahi daemon
        if avahi_status:
            enable_avahi()

        # Unmount root partition
        unmount(root_path)

    # Clean up
    status = clean_up()
    if not status:
        raise RuntimeError("Rm failed with exit status {}".format(status))
