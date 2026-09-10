#!/usr/bin/env python3
"""File organizer CLI: groups files in a directory by their extensions.

Usage:
    python file_organizer.py [-d DIRECTORY] [--dry-run]

Arguments:
    -d, --directory DIRECTORY  Target directory to organize (default: cwd).
    --dry-run                  Show what would be done without moving files.

The script iterates over entries in the directory, skips subdirectories,
determines the file extension (lowercase, without the leading dot). Files
without an extension are placed in a folder named "no_extension".
If the target folder does not exist, it is created. Existing files with
the same name in the target folder are renamed with a numeric suffix to
avoid overwriting.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Organize files by extension.")
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="Directory to organize (default: current working directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without moving files",
    )
    return parser.parse_args()


def get_extension(file_path: Path) -> str:
    """Return lowercase extension without the leading dot, or 'no_extension'."""
    suffix = file_path.suffix
    if not suffix:
        return "no_extension"
    # Remove leading dot and lower case
    return suffix[1:].lower()


def ensure_dir(dir_path: Path, dry_run: bool) -> None:
    """Create directory if it does not exist."""
    if dir_path.is_dir():
        return
    if dry_run:
        print(f"[dry-run] Would create directory: {dir_path}")
    else:
        dir_path.mkdir(parents=True, exist_ok=True)


def destination_path(target_dir: Path, filename: str, dry_run: bool) -> Path:
    """Return a non‑colliding destination path inside target_dir."""
    base = target_dir / filename
    if not base.exists():
        return base
    stem = base.stem
    suffix = base.suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = target_dir / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def organize_files(root: Path, dry_run: bool) -> None:
    for entry in root.iterdir():
        if not entry.is_file():
            continue  # Skip directories and special files
        ext = get_extension(entry)
        dest_dir = root / ext
        ensure_dir(dest_dir, dry_run)
        dest_file = destination_path(dest_dir, entry.name, dry_run)
        if dry_run:
            print(f"[dry-run] Would move: {entry} -> {dest_file}")
        else:
            try:
                shutil.move(str(entry), str(dest_file))
                print(f"Moved: {entry} -> {dest_file}")
            except Exception as e:
                print(f"Error moving {entry}: {e}", file=sys.stderr)


def main():
    args = parse_args()
    if not args.directory.is_dir():
        print(f"Error: {args.directory} is not a directory", file=sys.stderr)
        sys.exit(1)
    organize_files(args.directory, args.dry_run)


if __name__ == "__main__":
    main()