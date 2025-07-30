import os
import logging
logger = logging.getLogger(__name__)

"""
- Create directory listing from db
- Read directories and compare to previous list
- Lookup new files and add to database
"""


class Files:

    def __init__(self, root_dir):
        # Build a dictionary of directories {directory: [file1, file2, ...]
        self.root_dir = root_dir
        dirlist = os.walk(self.root_dir)
        self.dirs = {root: files for (root, dirs, files) in dirlist}

    def delta(self, comp_dirs_list: dict):
        # Compare the current file structure self.dirs to comp_dirs_list
        # Returns a delta list [{filename: {'action': action, 'dir', directory}]


    # Build a list of all added files to new_dirs and mark as added.  Skip duplicates...will be found later.
    # Iterate through old list to determine removed, moved or duplicate.

        files_delta = {}

        # Look through all the directories in the current files
        for directory in self.dirs:

            # Inspect all files added to this directory compared to the comp list
            file_list = self.dirs[directory]
            comp_list = comp_dirs_list.get(directory, [])
            added = [x for x in file_list if x not in comp_list]

            for f in added:
                if f in files_delta.keys():
                    # Duplicate file detected in multiple directories...will be handled in a subsequent pass
                    continue
                else:
                    # Enter the file to the files_delta list as "added" with the new directory
                    files_delta[f] = {'action': 'added',
                                      'dir': directory}

        # Look through all the directories of the comp list
        for directory in comp_dirs_list:

            # Inspect all files removed from each directory
            comp_list = comp_dirs_list[directory]
            file_list = self.dirs.get(directory, [])
            removed = [x for x in comp_list if x not in file_list]

            for f in comp_list:
                if f in files_delta.keys():
                    # If the file is already in the delta, it's been added to another directory

                    if f in file_list:
                        # File was duplicated elsewhere
                        files_delta[f]['action'] = 'duplicate'
                    else:
                        # File has been moved
                        files_delta[f]['action'] = 'moved'
                elif f not in file_list:
                    # If it's not, then it's been removed
                    files_delta[f] = {'action': 'removed',
                                      'dir': directory}

        print(files_delta)
        return files_delta
