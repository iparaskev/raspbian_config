"""__init__.py"""

import argparse
import os
from process_functions import *
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


if __name__ == "__main__":
    """Main programm"""

    args = parse_args()

    # Prepare folders
    prepare(args.image)

    # Get offsets of partitions.
    boot_offset, root_offset = process_fdisk_output(args.image)

    # Ask for ssh
    status = yes_no_question("ssh", "Do you want to enable ssh?")
    status = 0
    if status:
        # Mount boot partition
        mount_partition(args.image, boot_path, boot_offset)
        
        # Create ssh file
        enable_ssh()

        # Unmount boot partition
        unmount(boot_path)
    
    # Add wifi
    ssid = None
    psk = None
    wf_status = yes_no_question("wifi", "Connect to local wifi?")
    if wf_status:
        ssid = get_input("ssid", "Add ssid of wifi:")
        psk = get_input("psk", "Add password of wifi:")
        
    # Enable avahi daemon
    avahi_status = yes_no_question("avahi", "Enable avahi daemon?")
    
    # Or the binary options 
    mount_status = (wf_status | avahi_status)

    # If it needs to mount rootfs
    if mount_status:
        # Mount boot partition
        mount_partition(args.image, root_path, root_offset)

        # Check for wifi
        if wf_status:
            add_ssid_psk(ssid, psk)

        # Enable publish workstation of avahi daemon
        if avahi_status:
            enable_avahi()

        # Unmount root partition
        unmount(root_path)

    # Clean up
    status = clean_up()
    if not status:
        raise RuntimeError("Rm failed with exit status {}".format(status))
