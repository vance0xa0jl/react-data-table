"""
Tiny INI-style configuration parser.

This module provides a simple parser for INI-like files using only the
Python standard library. It supports sections, key=value pairs, and
comments starting with ';' or '#'. Blank lines are ignored.
"""

import sys
from typing import Dict, Any


def parse_ini(text: str) -> Dict[str, Dict[str, str]]:
    """
    Parse an INI-formatted string and return a nested dictionary.

    Parameters
    ----------
    text : str
        The INI content to parse.

    Returns
    -------
    dict
        A dictionary where each key is a section name and the value is
        another dictionary mapping option names to their values.
    """
    result: Dict[str, Dict[str, str]] = {}
    current_section: str = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue  # skip empty lines
        if line.startswith((';', '#')):
            continue  # skip comments

        if line.startswith('[') and line.endswith(']'):
            # New section
            current_section = line[1:-1].strip()
            if current_section not in result:
                result[current_section] = {}
            continue

        # Key=value pair
        if '=' not in line:
            # malformed line – ignore or could raise; we choose to ignore
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        if current_section is None:
            # Options without a section go into a default section named ''
            current_section = ''
            if current_section not in result:
                result[current_section] = {}
        result[current_section][key] = value

    return result


def _demo() -> None:
    """Run a simple demonstration when the script is executed directly."""
    sample = """
    ; Sample INI file
    [database]
    host = localhost
    port = 5432
    user = admin
    password = secret

    [logging]
    level = INFO
    file = /var/log/app.log
    """
    parsed = parse_ini(sample)
    for section, options in parsed.items():
        print(f"[{section}]")
        for key, val in options.items():
            print(f"{key} = {val}")
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = f.read()
    else:
        data = None
    if data is not None:
        config = parse_ini(data)
        for sect, opts in config.items():
            print(f"[{sect}]")
            for k, v in opts.items():
                print(f"{k} = {v}")
            print()
    else:
        _demo()