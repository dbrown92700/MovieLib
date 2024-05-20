import os

"""
- Create directory listing from db
- Read directories and compare to previous list
- Lookup new files and add to database
"""


class Files:

    def __init__(self, root_dir):
        self.root_dir = root_dir
        dirlist = os.walk(self.root_dir)
        self.dirs = {root: files for (root, dirs, files) in dirlist}

    def delta(self, comp_dirs_list: dict):

        files_delta = {
            'added': {},
            'removed': {}
        }
        for directory in self.dirs:
            file_list = self.dirs[directory]
            try:
                comp_files = comp_dirs_list[directory]
            except KeyError:
                files_delta['added'][directory] = file_list
                continue
            added = [x for x in comp_files if x not in file_list]
            if added:
                files_delta['removed'][directory] = added
            removed = [x for x in file_list if x not in comp_files]
            if removed:
                files_delta['added'][directory] = removed
        for directory in comp_dirs_list:
            if directory not in self.dirs.keys():
                files_delta['removed'][directory] = comp_dirs_list[directory]

        return files_delta
