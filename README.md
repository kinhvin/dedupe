# DeDupe

A simple Python CLI tool to find, back up, and remove duplicate files in a directory.

## What It Does

- Recursively scans a directory
- Groups files by size
- Hashes same-size candidates with `blake2b` (fast, secure, built into Python)
- Detects duplicates by matching hashes
- Keeps a duplicate copy from each duplicate group by default
- Lets you choose which duplicate entries to keep
- Copies removable duplicates to a backup folder before deleting

## Requirements

- Python 3.9+

No third-party dependencies.

## Run

```bash
python3 dedupe.py
