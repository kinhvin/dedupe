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
import hashlib
from collections import defaultdict

# Helper functions
def compute_file_hash(path, algorithm):
    """ Compute the hash of the file using the specified algorithm """
    hash_func = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def main():

    root = input("Enter the directory you want to search for duplicates in: ")

    # Sanitize the input path
    root = root.strip("'\"~$\/<>|?*")

    # Make sure it is a valid directory
    if not os.path.exists(root):
        print("The specified directory does not exist.")
        exit(1)
    if not os.path.isdir(root):
        print("The specified path is not a directory.")
        exit(1)

    # Initialize dicts
    by_size = defaultdict(list) # Store by size and path(s)
    by_hash = defaultdict(list) # Store by hash and path(s)
    dupes = []

    # Ask the user for the hash algorithm to use
    algorithm = input("Enter the hash algorithm to use (e.g., md5, sha1, sha256): ").lower()
    if algorithm not in hashlib.algorithms_available:
        print("The specified hash algorithm is not available.")
        algorithm = input("Enter the hash algorithm to use (e.g., md5, sha1, sha256): ").lower()

    # Group files by size while walking through the directory
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            by_size[os.path.getsize(path)].append(path)

    # Hash dupe candidates
    for paths in by_size.values():
        if len(paths) > 1:
            for p in paths:
                by_hash[compute_file_hash(p, algorithm)].append(p)
    
    # See if there are any possible dupes
    for paths in by_hash.values():
        if len(paths) > 1: # If there are more than 1 paths, they are likely dupes
            for p in paths:
                # Keep a copy of the first dupe
                if paths.index(p) != 0:
                    dupes.append(p)
    
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
        dupes.pop(i - ctr)
        ctr += 1

    # Delete what's left in the dupes list
    for f in dupes:
        print(f"Deleting {f} . . .")
        os.remove(f)

if __name__ == "__main__":
    main()