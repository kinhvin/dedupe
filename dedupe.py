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

# Search the directory
for dirpath, dirnames, filenames in os.walk(root):
    for name in filenames:
        full_path = os.path.join(dirpath, name)
        print(full_path)