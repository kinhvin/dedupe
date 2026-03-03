""" 
Program designed to search for duplicates in a directory, 
mark them for deletion and delete them accordingly
 """

""" 
Steps 
1. Search for duplicates in the chosen directory
2. Mark duplicates for deletion
3. Keep a copy of each duplicate file by default
4. Prompt the user to choose duplicate files they would like to keep
5. Backup the files that are going to be deleted
6. Delete the remaining duplicates
"""

import os
import shutil
import uuid
from pathlib import Path
import hashlib
from collections import defaultdict
import questionary
from questionary import Choice
from tkinter import filedialog

""" Consts """
TYPED_MODE = "typed"
BROWSE_MODE = "browse"
EXIT_CHOICE = "exit"
RETRY_CHOICE = "retry"

""" Validate that the inputted directory is valid """
def validate_dir(path):
    sanitized_path = Path(os.path.expanduser(os.path.expandvars(path.strip("'").strip('"'))))
    return True if sanitized_path.is_dir() else "Please enter an existing directory."

""" Prompt the user for the directory they want to search for duplicates in """
def prompt_root():
    mode = questionary.select(
        "Choose one:",
        choices=[
            Choice("Type a path", value=TYPED_MODE),
            Choice("Browse folders", value=BROWSE_MODE),
            Choice("Exit", value=EXIT_CHOICE)
        ],
    ).ask()

    if mode in {EXIT_CHOICE, None}:
        return None

    elif mode == TYPED_MODE:
        while True:
            raw = questionary.path(
                "Enter the path to the directory you want to search for duplicates in:",
                only_directories=True,
                validate=validate_dir,
                ).ask()

            # User canceled the prompt
            if raw is None:
                return None
            
            # Sanitize / normalize the path
            root = Path(os.path.expanduser(os.path.expandvars(raw.strip("'").strip('"'))))

            # Return the absolute normalized path
            if root.is_dir():
                return root.resolve()
            print("Invalid directory. Try again.")

    elif mode == BROWSE_MODE:
        while True:
            raw = filedialog.askdirectory(initialdir=Path.cwd(), mustexist=True)
            
            # User selected a folder
            if raw:
                return Path(raw).resolve()

            # Handle cancellation
            if not raw:
                choice = questionary.select(
                    "No folder selected. What next?",
                    choices=[
                        Choice("Choose again", value=RETRY_CHOICE),
                        Choice("Exit program", value=EXIT_CHOICE),
                    ]
                ).ask()
                if choice == RETRY_CHOICE:
                    continue
                else:
                    return None

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
    if root is None:
        print("Exiting program...")
        exit(0)
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
    # mode = questionary.select(
    #     "Choose one:",
    #     choices=[
    #         Choice("Type a path", value=TYPED_MODE),
    #         Choice("Browse folders", value=BROWSE_MODE),
    #         Choice("Exit", value=EXIT_CHOICE)
    #     ],
    # )
    choices = questionary.checkbox('' \
    'Please choose what files to keep, enter if none',
    choices=dupes
    ).ask()

    # Remove the chosen files to keep from the dupes list
    ctr = 1 # Keep track of each file that is removed to account for changing size
    for path in choices:
        print(f"Keeping {path} . . .")
        dupes.remove(path)
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
