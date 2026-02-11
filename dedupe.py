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

from importlib.metadata import files
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
    files_size = {} # Store by path and size
    files_hash = {} # Store by path and hash
    by_size = defaultdict(list) # Store by size and path(s)
    by_hash = defaultdict(list) # Store by hash and path(s)
    dupes = []
    to_clean = []

    # Ask the user for the hash algorithm to use
    algorithm = input("Enter the hash algorithm to use (e.g., md5, sha1, sha256): ").lower()
    if algorithm not in hashlib.algorithms_available:
        print("The specified hash algorithm is not available.")
        algorithm = input("Enter the hash algorithm to use (e.g., md5, sha1, sha256): ").lower()

    # Search the directory
    for dirpath, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            # print(path) # Testing

            # Get the file size (bytes) and store it in the dict
            size = os.path.getsize(path)
            files_size[path] = size
            # print(files_size) # Testing

    # Store the paths of files with the same size in a dict
    for path, size in files_size.items():
        by_size[size].append(path)
        print(by_size) # Testing

    # Compute the hash of files with the same size and store it in a dict
    for size, path in by_size.items():
        if len(path) > 1: # Only compute hash for files with the same size
            for p in path:
                file_hash = compute_file_hash(p, algorithm)
                files_hash[p] = file_hash
                print(files_hash) # Testing

    # Store paths based on hash
    for path, hash in files_hash.items():
        by_hash[hash].append(path)
        print(by_hash)
    
    # See if there are any possible dupes
    for hash, path in by_hash.items():
        if len(path) > 1: # If there are more than 1 paths, they are likely dupes
            for p in path:
                dupes.append(p)
    
    # Prompt user to select files to cleanup
    for i, d in enumerate(dupes, start=1): # Provide the user with a numbered list of the dupes
        print(f"{i}. {d}")
    choices = input("Enter the index of the files to clean up: ")

    # Append the chosen files to the to_clean list
    for c in choices.split(","):
        c = c.strip()
        if c.isdigit():
            i = int(c) - 1
            if 0 <= i < len(dupes):
                to_clean.append(dupes[i])
    print(to_clean) # Testing

    # Delete each file in the to_clean list
    for f in to_clean:
        os.remove(f)

if __name__ == "__main__":
    main()