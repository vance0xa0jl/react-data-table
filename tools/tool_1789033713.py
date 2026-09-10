#!/usr/bin/env python3
"""
Tiny INI-style config parser.

This module provides a simple function `parse_ini` that reads a string or
file-like object containing INI‑formatted data and returns a nested
dictionary: {section: {key: value, ...}, ...}.  Sections are denoted by
lines like `[section]`.  Keys and values are separated by `=`; surrounding
whitespace is stripped.  Lines starting with `#` or `;` are treated as
comments and ignored.  Blank lines are also ignored.

Example usage:

    >>> ini_text = \"\"\"\n    [database]\n    host = localhost\n    port = 5432\n    ; user comment\n    \"\"\"\n    >>> parse_ini(ini_text)\n    {'database': {'host': 'localhost', 'port': '5432'}}\n"""

import sys
from typing import Dict, Any, TextIO

def parse_ini(source: Any) -> Dict[str, Dict[str, str]]:
    """Parse INI‑style text from *source* and return a dict of sections.

    *source* can be a string, a path‑like object, or any object with a
    ``read()`` method (e.g. an open file).  If a string is given and it
    contains newlines it is treated as the raw INI content; otherwise it
    is interpreted as a file path and opened for reading.

    Returns:
        A dictionary mapping section names to dictionaries of key/value
        pairs.  If no section header is encountered, items are placed
        under the special key ``None`` (which callers can ignore or
        treat as a global section).
    """
    # Obtain a file‑like object to iterate over lines.
    if hasattr(source, "read"):
        lines = source
    elif isinstance(source, (bytes, bytearray)):
        # Decode bytes to text using UTF-8.
        lines = source.decode("utf-8").splitlines()
    elif isinstance(source, str):
        # If the string looks like a path (no newline) treat as filename.
        if "\n" not in source and "\r" not in source:
            try:
                with open(source, "r", encoding="utf-8") as f:
                    lines = f
            except OSError:
                # Fallback: treat the string as raw content.
                lines = source.splitlines()
        else:
            lines = source.splitlines()
    else:
        raise TypeError("source must be a file‑like object, str, or bytes")

    result: Dict[str, Dict[str, str]] = {}
    current_section = None
    # Ensure a dict exists for the current section (create on demand).
    def get_section_dict():
        if current_section not in result:
            result[current_section] = {}
        return result[current_section]

    for raw_line in lines:
        # Strip trailing newline characters but keep leading/trailing spaces
        # for now; we will strip them later as needed.
        line = raw_line.rstrip("\n\r")
        # Remove inline whitespace for empty/comment detection.
        stripped = line.strip()
        if not stripped:
            # Blank line.
            continue
        if stripped[0] in ("#", ";"):
            # Comment line.
            continue
        # Section header?
        if stripped.startswith("[") and stripped.endswith("]"):
            section_name = stripped[1:-1].strip()
            current_section = section_name
            # Ensure entry exists.
            get_section_dict()
            continue
        # Key‑value pair.
        if "=" not in line:
            # malformed line – ignore or could raise; we choose to ignore.
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        # If we haven't seen a section yet, use None as a default.
        if current_section is None:
            current_section = None
        get_section_dict()[key] = value
    return result

def _demo() -> None:
    """Simple demonstration when run as a script."""
    sample = """
    [database]
    host = localhost
    port = 5432
    ; user comment
    username = admin
    password = secret

    [logging]
    level = INFO
    file = /var/log/app.log
    """
    parsed = parse_ini(sample)
    import pprint
    pprint.pprint(parsed)

if __name__ == "__main__":
    _demo()