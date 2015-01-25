#!/usr/bin/env python
# encoding: utf-8

"""Copy a website into Freenet -- either a single page or the full site.

A bridge between wget and pyFreenet."""

import argparse
import fcp
import os
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("site", help="the URL to the website to copy")
parser.add_argument("-d", "--target-directory",
                   default=None,
                   help="target directory (default: host part of the path)")
parser.add_argument("--single-page", action="store_true",
                   default=False,
                   help="target directory (default: host part of the path)")

args = parser.parse_args()

wget_program = "wget"

wget_mode_option_lists = {
    "mirror": ["-m", "-nc", "-N", "-k", "-p", "-np", "-nH", "-nd", "-E", "--no-check-certificate", "-e", "robots=off", "-U", "'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"],
    "single_page": ["-t", "2", "-np", "-N", "-k", "-p", "-nd", "-nH", "-H", "-E", "--no-check-certificate", "-e", "robots=off", "-U", "'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4'"],
}

wget_options = {
    "target_directory": "--directory-prefix={}"
}

command = [wget_program]
if args.single_page:
    command.extend(wget_mode_option_lists["single_page"])
else:
    command.extend(wget_mode_option_lists["mirror"])

if args.target_directory:
    command.append(wget_options["target_directory"].format(
        args.target_directory))
else:
    is_right_directory = raw_input("You did not specify a target directory. The site will be written in the current directory. Are you in the directory in which the site should be written? (current directory: {}) (Yes/no)".format(os.getcwd())).strip().lower() in ["y", "yes"]
    if not is_right_directory:
        sys.exit(1)

print args

