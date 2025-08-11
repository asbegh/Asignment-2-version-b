#!/usr/bin/env python3

import subprocess
import sys
import argparse

'''
OPS445 Assignment 2
Program: duim.py
Author: Amaanbhai Salimbhai Begh 
The python code in this file (duim.py) is original work written by
AmaanbhaiSalimbhaiBegh. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script replicates and enhances the functionality of the `du` command 
by generating a user-friendly disk usage report with bar charts.

Date: 2023
'''

def parse_command_args():
    """Sets up argparse for handling command-line arguments."""
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Print sizes in human-readable format (e.g., 1K, 23M, 2G).")
    parser.add_argument("target", nargs="?", default=".", help="The directory to scan. Default is the current directory.")
    return parser.parse_args()

def percent_to_graph(percent: int, total_chars: int) -> str:
    """
    Converts a percentage into a bar graph representation.
    :param percent: The percentage to represent (0-100).
    :param total_chars: The total number of characters in the bar.
    :return: A string representing the bar graph.
    """
    if percent < 0 or percent > 100:
        raise ValueError("Percentage must be between 0 and 100.")
    filled_length = int(round(percent * total_chars / 100))
    return "=" * filled_length + " " * (total_chars - filled_length)

def call_du_sub(location: str) -> list:
    """
    Uses subprocess to call `du -d 1 <location>` and returns the raw output as a list.
    Handles permission errors gracefully by skipping inaccessible directories.
    :param location: The target directory for `du`.
    :return: A list of strings, each containing size and directory path.
    """
    try:
        result = subprocess.Popen(["du", "-d", "1", location], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        if stderr:
            print(f"Warning: {stderr.strip()}", file=sys.stderr)
        if result.returncode != 0:
            return []  # Return an empty list on error instead of exiting
        return stdout.strip().split("\n")
    except FileNotFoundError:
        print("Error: `du` command not found. Ensure it's installed on your system.", file=sys.stderr)
        return []

def create_dir_dict(raw_dat: list) -> dict:
    """
    Converts raw output from `du` into a dictionary of directory sizes.
    :param raw_dat: A list of strings from the output of `du`.
    :return: A dictionary with directories as keys and sizes (in bytes) as values.
    """
    dir_dict = {}
    for line in raw_dat:
        try:
            size, path = line.split("\t", 1)
            dir_dict[path] = int(size)
        except ValueError:
            continue  # Skip lines that don't match the expected format
    return dir_dict

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    """
    Converts a size in kibibytes into a human-readable format (e.g., MiB, GiB).
    :param kibibytes: The size in kibibytes.
    :param decimal_places: The number of decimal places for the formatted size.
    :return: A string representing the size in a human-readable format.
    """
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
    target_dir = args.target

    # Get raw data from `du`
    raw_data = call_du_sub(target_dir)
    if not raw_data:
        print(f"Error: Unable to retrieve data for directory {target_dir}")
        sys.exit(1)

    # Convert raw data into a dictionary
    dir_data = create_dir_dict(raw_data)

    # Calculate total size
    total_size = sum(dir_data.values())

    # Print report
    print(f"Total: {bytes_to_human_r(total_size) if args.human_readable else total_size} bytes   {target_dir}")
    for path, size in dir_data.items():
        percent = (size / total_size) * 100 if total_size else 0
        graph = percent_to_graph(percent, args.length)
        size_display = bytes_to_human_r(size) if args.human_readable else f"{size} bytes"
        print(f"{percent:3.0f}% [{graph}] {size_display} {path}")

