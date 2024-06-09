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
        self.root_dir = root_dir
        dirlist = os.walk(self.root_dir)
        self.dirs = {root: files for (root, dirs, files) in dirlist}

    def delta(self, comp_dirs_list: dict):

        files_delta = {}
        for directory in self.dirs:
            file_list = self.dirs[directory]
            try:
                comp_list = comp_dirs_list[directory]
            except KeyError:
                comp_list = []
            removed = [x for x in comp_list if x not in file_list]
            for f in removed:
                if f in files_delta.keys():
                    if files_delta[f]['action'] == 'removed':
                        continue
                    else:
                        files_delta[f]['action'] = 'moved'
                        files_delta[f]['dir'] = directory
                else:
                    files_delta[f] = {'action': 'removed',
                                      'dir': directory}
            added = [x for x in file_list if x not in comp_list]
            for f in added:
                if f in files_delta.keys():
                    if files_delta[f]['action'] == 'added':
                        continue
                    else:
                        files_delta[f]['action'] = 'moved'
                        files_delta[f]['dir'] = directory
                else:
                    files_delta[f] = {'action': 'added',
                                      'dir': directory}
        for directory in comp_dirs_list:
            if directory not in self.dirs.keys():
                for f in comp_dirs_list[directory]:
                    if f in files_delta.keys():
                        if files_delta[f]['action'] == 'removed':
                            continue
                        else:
                            files_delta[f]['action'] = 'moved'
                    else:
                        files_delta[f] = {'action': 'removed',
                                          'dir': directory}

        return files_delta

    # def delta(self, comp_dirs_list: dict):
    #
    #     files_delta = {
    #         'added': {},
    #         'removed': {},
    #         'moved': {}
    #     }
    #     for directory in self.dirs:
    #         file_list = self.dirs[directory]
    #         try:
    #             comp_files = comp_dirs_list[directory]
    #         except KeyError:
    #             files_delta['added'][directory] = file_list
    #             continue
    #         removed = [x for x in comp_files if x not in file_list]
    #         if removed:
    #             files_delta['removed'][directory] = removed
    #         added = [x for x in file_list if x not in comp_files]
    #         if added:
    #             files_delta['added'][directory] = added
    #     for directory in comp_dirs_list:
    #         if directory not in self.dirs.keys():
    #             files_delta['removed'][directory] = comp_dirs_list[directory]
    #
    #     return files_delta
