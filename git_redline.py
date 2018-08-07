# import subprocess
import sys
import os
import shutil


class Repo(object):
    def __init__(self, hash, path_to_redline_prefs, temp_dir, flag=False):
        self.hash = hash
        self.flag = flag
        self.temp_dir = temp_dir
        self.prefs = path_to_redline_prefs
        self.repo_path = os.path.join(temp_dir, 'git_redline', (flag + '_' + hash))

    def clone(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)
        os.makedirs(self.repo_path, exist_ok=True)
        # clone_path =
        pass


def parse_command_line(argv):
    if len(argv) < 4 or len(argv) > 5:
        raise ValueError(
            '''git_redline.py takes  either three or four arguments.\n
            Use python git_redline.py <path_to_redline_prefs.txt>
            <hash_from> <hash_to> <path_to_temporary_directory>''')
    path_to_redline_prefs = os.path.expanduser(argv[1])
    hash_from = argv[2]
    hash_to = argv[3]
    if len(argv) == 5:
        path_to_temporary_directory = os.path.expanduser(argv[4])
    else:
        path_to_temporary_directory = os.path.expanduser(
            '~/Documents/temporary')
    return (path_to_redline_prefs, hash_from,
            hash_to, path_to_temporary_directory)


if __name__ == '__main__':
    (path_to_redline_prefs, hash_from, hash_to,
        path_to_temporary_directory) = parse_command_line(
        sys.argv)
    repo_from = Repo(hash_from, path_to_redline_prefs,
                     path_to_temporary_directory, 'from')
    repo_from.clone()
    # print(vars(repo_from))
    repo_to = Repo(hash_to, path_to_redline_prefs,
                   path_to_temporary_directory, 'to')
    repo_to.clone()
