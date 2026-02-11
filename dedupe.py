""" 
Program designed to search for duplicates in a directory, 
mark them for deletion and delete them accordingly
 """

""" 
Steps 
1. Search for duplicates in the directory
2. Mark duplicates for deletion
3. Delete the marked duplicates accordingly based on what the user wants to do with them
"""

import os
import shutil
import uuid
from pathlib import Path
import hashlib
from collections import defaultdict

""" Prompt the user for the directory they want to search for duplicates in """
def prompt_root() -> Path:
    while True:
        raw = input("Enter the directory you want to search for duplicates in: ").strip()

        # Check that they actually inputted a path
        if not raw:
            print("Path cannot be empty.")
            continue

        # Remove wrapping quotes
        raw = raw.strip("'").strip('"')

        # Expand ~ and env vars then normalize
        expanded = os.path.expanduser(os.path.expandvars(raw))
        path = Path(expanded)

        # Return the absolute normalized path
        if path.is_dir():
            return path.resolve()
        print("Invalid directory. Try again.")

""" Compute the hash of an individual file using the chosen hashing algorithm """
def compute_file_hash(path, algorithm="blake2b") -> str:
    hash_func = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

""" Create a backup directory with a unique token """
def create_backup_dir(prefix="dupes_backup", root=Path.cwd()) -> Path:
    while True:
        # Generate a unique token to append to the end of the backup dir
        token = uuid.uuid4()
        backup_dir = root / f"{prefix}_{token}"

        # Create the backup
        try:
            os.mkdir(backup_dir)
            return backup_dir
        except FileExistsError:
            pass

def main():

    root = prompt_root()
    print(f"Searching for duplicates in {root}")

    # Initialize dicts
    by_size = defaultdict(list) # Store by size and path(s)
    by_hash = defaultdict(list) # Store by hash and path(s)
    dupes = []

    # Group files by size while walking through the directory
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            by_size[os.path.getsize(path)].append(path)

    # Hash dupe candidates
    for paths in by_size.values():
        if len(paths) > 1:
            for p in paths:
                by_hash[compute_file_hash(p)].append(p)
    
    # See if there are any possible dupes
    for paths in by_hash.values():
        if len(paths) > 1: # If there are more than 1 paths, they are likely dupes
            for p in paths:
                # Keep a copy of the first dupe
                if paths.index(p) != 0:
                    dupes.append(p)

    # No duplicates
    if len(dupes) < 1:
        print("No duplicates are present, terminating the program . . .")
        exit(0)
    
    # Prompt user to select files they would like to keep
    for i, d in enumerate(dupes, start=1): # Provide the user with a numbered list of the dupes
        print(f"{i}. {d}")
    choices = input("Enter the indexes of the files you would like to keep (enter if none): ")

    # Sort the user input into individual indexes
    indexes = []
    for c in choices.split(","):
        c = c.strip()
        if c.isdigit():
            i = int(c)
            if 1 <= i <= len(dupes):
                indexes.append(i)
    indexes = sorted(set(indexes))

    # Remove the chosen files to keep from the dupes list
    ctr = 1 # Keep track of each file that is removed to account for changing size
    for i in indexes:
        print(f"Keeping {dupes.pop(i - ctr)} . . .")
        ctr += 1

    # Create a backup dir
    backup_dir = create_backup_dir()
    print(f"Created {backup_dir}")

    # Copy the dupes over to the backup
    print(f"Backing up duplicates in {backup_dir}")
    for d in dupes:
        print(f"Backed up {d}")
        shutil.copy(d, backup_dir)

    # Delete what's left in the dupes list
    for d in dupes:
        print(f"Deleting {d} . . .")
        os.remove(d)

if __name__ == "__main__":
    main()