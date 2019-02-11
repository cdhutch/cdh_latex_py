import subprocess
import sys
import os
import shutil
# import compile_tex
import expand_tex
import latex_diff
import re
from ast import literal_eval


class Prefs(object):

    def __init__(self, path_to_redline_prefs):
        f = open(path_to_redline_prefs)
        self.url = None
        self.subdir = None
        self.build_py = None
        self.fname_md = None
        self.fname_csv = None
        self.l_flavors = ['']
        self.branch = None
        self.repo_top = None
        self.repo_subdir = None
        for line in f:
            pattern = re.compile(r'^URL:\s', re.IGNORECASE)
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.url = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'^Subdir:\s', re.IGNORECASE)
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.subdir = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'build_py:\s', re.IGNORECASE)
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.build_py = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'fname_md:\s', re.IGNORECASE)
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.fname_md = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'fname_csv:\s', re.IGNORECASE)
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.fname_csv = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'l_flavors:\s', re.IGNORECASE)
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.l_flavors = literal_eval(pattern.split(line)[1])
                continue
            pattern = re.compile(r'branch:\s')
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.branch = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'repo_top:\s')
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.repo_top = pattern.split(line)[1].strip()
                continue
            pattern = re.compile(r'repo_subdir:\s')
            pattern_split = pattern.split(line)
            if len(pattern_split) > 1:
                self.repo_subdir = pattern.split(line)[1].strip()
                continue
        f.close()
        if self.url is None:
            raise ValueError('Need a url field in ' + path_to_redline_prefs)
        if (self.subdir is None) & (self.repo_top is None):
            raise ValueError(
                'Need a subdir or repo_top field in ' + path_to_redline_prefs)
        if self.subdir is None:
            self.subdir = os.path.join(self.repo_top, self.repo_subdir)
        if self.build_py is None:
            raise ValueError('Need a build_py field in ' +
                             path_to_redline_prefs)
        # if fname_md is None:
        #     raise ValueError('Need a fname_md field in ' + path_to_redline_prefs)
        # if fname_csv is None:
        #     raise ValueError(
        #       'Need a fname_csv field in ' + path_to_redline_prefs)
        # return (url, subdir, build_py, fname_md, fname_csv, l_flavors,
            # repo_top, repo_subdir, branch)


class Repo(object):
    # def __init__(self, hash, path_to_redline_prefs, temp_dir, url, subdir,
    #              build_py, fname_md, fname_csv, branch, repo_top, repo_subdir, flag=False,
    #              l_flavors=[]):
    def __init__(self, redline_prefs, hash, flag=False):
        self.hash = hash
        # self.temp_dir = redline_prefs.path_to_temporary_directory
        # self.prefs = path_to_redline_prefs
        self.diff_path = os.path.join(
            redline_prefs.path_to_temporary_directory, 'git_redline',
            'diff_results')
        self.repo_path = os.path.join(
            redline_prefs.path_to_temporary_directory, 'git_redline',
            (flag + '_' + hash)).strip()
        # self.url = url
        # self.subdir = subdir
        # self.build_py = build_py
        # self.fname_md = fname_md
        # self.fname_csv = fname_csv
        # self.branch = branch
        self.flag = flag
        self.redline_prefs = redline_prefs
        # self.l_flavors = l_flavors
        # self.repo_top = repo_top
        # self.repo_subdir = repo_subdir

    def clone(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)
        os.makedirs(self.repo_path, exist_ok=True)
        # cwd_orig = os.getcwd()
        os.chdir(self.repo_path)
        subprocess.run(['git', 'clone', self.redline_prefs.url])
        str_cmd = 'git clone ' + self.redline_prefs.url
        print(str_cmd)
        if self.redline_prefs.repo_top is not None:
            os.chdir(self.redline_prefs.repo_top)
        if self.redline_prefs.branch is not None:
            subprocess.run(['git', 'checkout', self.redline_prefs.branch])
        str_cmd = 'cd '
        # print(self.redline_prefs.subdir)
        if self.redline_prefs.repo_top is not None:
            # os.chdir(os.path.join(self.redline_prefs.repo_top,
            #                       self.redline_prefs.repo_subdir))
            os.chdir(self.redline_prefs.repo_subdir)
            str_cmd += self.redline_prefs.repo_subdir
        else:
            os.chdir(os.path.join(self.redline_prefs.repo_path,
                                  self.redline_prefs.subdir))
            str_cmd += self.redline_prefs.subdir
        print(str_cmd)
        subprocess.run(['git', 'reset', '--hard', self.hash])
        str_cmd = 'git reset --hard ' + self.hash
        print(str_cmd)

    def generate_expanded_tex(self, flavor):
        # build_full_path = os.path.join(
        #     self.repo_path, self.subdir, self.build_py).strip()
        os.chdir(os.path.join(self.repo_path, self.redline_prefs.subdir))
        md_full_path = os.path.join(
            self.repo_path, self.redline_prefs.subdir,
            self.redline_prefs.fname_md).strip()
        # csv_full_path = os.path.join(
        #     self.repo_path, self.subdir, self.fname_csv).strip()
        # tex_full_path = os.path.splitext(
        #     md_full_path)[0] + '_supplemental' + '.tex'
        tex_full_path = os.path.splitext(
            md_full_path)[0] + flavor + '.tex'
        print(os.getcwd())
        build_cmd = ['python', self.redline_prefs.build_py,
                     # self.fname_md, self.fname_csv, self.repo_path]
                     # self.fname_md, self.repo_path]
                     ]
        build_cmd = list(filter(None, build_cmd))
        print('----')
        print(build_cmd)
        print('----')
        subprocess.run(build_cmd)
        build_cmd = ['python', 'expand_tex.py', tex_full_path]
        print(build_cmd)
        self.expanded_path = expand_tex.main([None, tex_full_path])
        # subprocess.run(build_cmd)


def run_diff(repo_from, repo_to, flavor, preserve_diff=True):
    latex_diff.main([None, repo_from.expanded_path,
                     repo_to.expanded_path, (repo_from.diff_path + flavor)],
                    hash_from=repo_from.hash, hash_to=repo_to.hash,
                    flavor=flavor, preserve_diff=preserve_diff)


def parse_prefs_file(path_to_redline_prefs):
    f = open(path_to_redline_prefs)
    url = None
    subdir = None
    build_py = None
    fname_md = None
    fname_csv = None
    l_flavors = ['']
    branch = None
    repo_top = None
    repo_subdir = None
    for line in f:
        pattern = re.compile(r'^URL:\s', re.IGNORECASE)
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            url = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'^Subdir:\s', re.IGNORECASE)
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            subdir = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'build_py:\s', re.IGNORECASE)
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            build_py = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'fname_md:\s', re.IGNORECASE)
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            fname_md = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'fname_csv:\s', re.IGNORECASE)
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            fname_csv = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'l_flavors:\s', re.IGNORECASE)
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            l_flavors = literal_eval(pattern.split(line)[1])
            continue
        pattern = re.compile(r'branch:\s')
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            branch = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'repo_top:\s')
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            repo_top = pattern.split(line)[1].strip()
            continue
        pattern = re.compile(r'repo_subdir:\s')
        pattern_split = pattern.split(line)
        if len(pattern_split) > 1:
            repo_subdir = pattern.split(line)[1].strip()
            continue

    f.close()
    if url is None:
        raise ValueError('Need a url field in ' + path_to_redline_prefs)
    if (subdir is None) & (repo_top is None):
        raise ValueError('Need a subdir field in ' + path_to_redline_prefs)
    if build_py is None:
        raise ValueError('Need a build_py field in ' + path_to_redline_prefs)
    # if fname_md is None:
    #     raise ValueError('Need a fname_md field in ' + path_to_redline_prefs)
    # if fname_csv is None:
    #     raise ValueError(
    #       'Need a fname_csv field in ' + path_to_redline_prefs)
    return (url, subdir, build_py, fname_md, fname_csv, l_flavors,
            repo_top, repo_subdir, branch)


def parse_command_line(argv):
    if len(argv) < 4 or len(argv) > 5:
        raise ValueError(
            '''git_redline.py takes  either three or four arguments.\n
            Use python git_redline.py <path_to_redline_prefs.txt>
            <hash_from> <hash_to> <path_to_temporary_directory>''')
    path_to_redline_prefs = os.path.expanduser(argv[1])
    redline_prefs = Prefs(path_to_redline_prefs)
    # f = open(path_to_redline_prefs)
    # url = f.readline().strip()
    # subdir = f.readline().strip()
    # build_py = f.readline().strip()
    # fname_md = f.readline().strip()
    # fname_csv = f.readline().strip()
    hash_from = argv[2]
    hash_to = argv[3]
    if len(argv) == 5:
        redline_prefs.path_to_temporary_directory = os.path.expanduser(argv[4])
    else:
        redline_prefs.path_to_temporary_directory = os.path.expanduser(
            '~/Documents/temporary')
    return redline_prefs, hash_from, hash_to


if __name__ == '__main__':
    redline_prefs, hash_from, hash_to = parse_command_line(sys.argv)
    shutil.rmtree(
        redline_prefs.path_to_temporary_directory, ignore_errors=True)
    # repo_from = Repo(hash_from, path_to_redline_prefs,
    #                  path_to_temporary_directory, url, subdir,
    #                  build_py, fname_md, fname_csv, branch,
    #                  repo_top, repo_subdir, 'from')
    repo_from = Repo(redline_prefs, hash_from, 'from')
    repo_from.clone()
    # print(vars(repo_from))
    # repo_to = Repo(hash_to, path_to_redline_prefs,
    #                path_to_temporary_directory, url, subdir,
    #                build_py, fname_md, fname_csv, branch,
    #                repo_top, repo_subdir, 'to')
    repo_to = Repo(redline_prefs, hash_to, 'to')
    repo_to.clone()
    for flavor in redline_prefs.l_flavors:
        repo_from.generate_expanded_tex(flavor)
        repo_to.generate_expanded_tex(flavor)
        run_diff(repo_from, repo_to, flavor)
