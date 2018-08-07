import subprocess
import sys
import os
import shutil


class Repo(object):
    def __init__(self, hash, path_to_redline_prefs, temp_dir, url, subdir, build_py, fname_md, fname_csv, flag=False):
        self.hash = hash
        self.temp_dir = temp_dir
        self.prefs = path_to_redline_prefs
        self.repo_path = os.path.join(
            temp_dir, 'git_redline', (flag + '_' + hash))
        self.url = url
        self.subdir = subdir
        self.build_py = build_py
        self.fname_md = fname_md
        self.fname_csv = fname_csv
        self.flag = flag

    def clone(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)
        os.makedirs(self.repo_path, exist_ok=True)
        cwd_orig = os.getcwd()
        os.chdir(self.repo_path)
        subprocess.run(['git', 'clone', self.url])
        str_cmd = 'git clone ' + self.url
        print(str_cmd)
        str_cmd = 'cd ' + subdir
        print(subdir)
        os.chdir(os.path.join(self.repo_path, subdir))
        subprocess.run(['git', 'reset', '--hard', self.hash])
        str_cmd = 'git reset --hard ' + self.hash
        print(str_cmd)


def parse_command_line(argv):
    if len(argv) < 4 or len(argv) > 5:
        raise ValueError(
            '''git_redline.py takes  either three or four arguments.\n
            Use python git_redline.py <path_to_redline_prefs.txt>
            <hash_from> <hash_to> <path_to_temporary_directory>''')
    path_to_redline_prefs = os.path.expanduser(argv[1])
    f = open(path_to_redline_prefs)
    url = f.readline().strip()
    subdir = f.readline().strip()
    build_py = f.readline()
    fname_md = f.readline()
    fname_csv = f.readline()
    hash_from = argv[2]
    hash_to = argv[3]
    if len(argv) == 5:
        path_to_temporary_directory = os.path.expanduser(argv[4])
    else:
        path_to_temporary_directory = os.path.expanduser(
            '~/Documents/temporary')
    return (path_to_redline_prefs, hash_from,
            hash_to, path_to_temporary_directory, url, subdir,
            build_py, fname_md, fname_csv)


if __name__ == '__main__':
    (path_to_redline_prefs, hash_from, hash_to,
        path_to_temporary_directory, url, subdir, build_py,
        fname_md, fname_csv) = parse_command_line(
        sys.argv)
    repo_from = Repo(hash_from, path_to_redline_prefs,
                     path_to_temporary_directory, url, subdir, build_py, fname_md, fname_csv, 'from')
    repo_from.clone()
    # print(vars(repo_from))
    repo_to = Repo(hash_to, path_to_redline_prefs,
                   path_to_temporary_directory, url, subdir, build_py, fname_md, fname_csv, 'to')
    repo_to.clone()
