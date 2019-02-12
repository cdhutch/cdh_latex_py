import subprocess
import sys
import os
import shutil
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
        self.path_to_temporary_directory = os.path.expanduser(
            '~/Documents/temporary')

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


class Repo(object):
    def __init__(self, repo_redline_prefs, repo_hash, flag=None):
        self.redline_prefs = repo_redline_prefs
        self.hash = repo_hash
        self.diff_path = os.path.join(
            redline_prefs.path_to_temporary_directory, 'git_redline',
            'diff_results')
        self.repo_path = os.path.join(
            redline_prefs.path_to_temporary_directory, 'git_redline',
            (flag + '_' + repo_hash)).strip()
        self.flag = flag
        self.expanded_path = None

    def clone(self):
        shutil.rmtree(self.repo_path, ignore_errors=True)
        os.makedirs(self.repo_path, exist_ok=True)
        os.chdir(self.repo_path)
        subprocess.run(['git', 'clone', self.redline_prefs.url])
        str_cmd = 'git clone ' + self.redline_prefs.url
        print(str_cmd)
        if self.redline_prefs.repo_top is not None:
            os.chdir(self.redline_prefs.repo_top)
        if self.redline_prefs.branch is not None:
            subprocess.run(['git', 'checkout', self.redline_prefs.branch])
        str_cmd = 'cd '
        if self.redline_prefs.repo_top is not None:
            os.chdir(self.redline_prefs.repo_subdir)
            str_cmd += self.redline_prefs.repo_subdir
        else:
            os.chdir(os.path.join(self.repo_path,
                                  self.redline_prefs.subdir))
            str_cmd += self.redline_prefs.subdir
        print(str_cmd)
        subprocess.run(['git', 'reset', '--hard', self.hash])
        str_cmd = 'git reset --hard ' + self.hash
        print(str_cmd)

    def generate_expanded_tex(self, doc_flavor):
        os.chdir(os.path.join(self.repo_path, self.redline_prefs.subdir))
        md_full_path = os.path.join(
            self.repo_path, self.redline_prefs.subdir,
            self.redline_prefs.fname_md).strip()
        tex_full_path = os.path.splitext(
            md_full_path)[0] + doc_flavor + '.tex'
        print(os.getcwd())
        build_cmd = ['python', self.redline_prefs.build_py]
        build_cmd = list(filter(None, build_cmd))
        print('----')
        print(build_cmd)
        print('----')
        subprocess.run(build_cmd)
        build_cmd = ['python', 'expand_tex.py', tex_full_path]
        print(build_cmd)
        self.expanded_path = expand_tex.main([None, tex_full_path])


def run_diff(diff_repo_from, diff_repo_to, doc_flavor, preserve_diff=True):
    latex_diff.main([None, diff_repo_from.expanded_path,
                     diff_repo_to.expanded_path, (diff_repo_from.diff_path + doc_flavor)],
                    hash_from=diff_repo_from.hash, hash_to=diff_repo_to.hash,
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
    return (url, subdir, build_py, fname_md, fname_csv, l_flavors,
            repo_top, repo_subdir, branch)


def parse_command_line(argv):
    if len(argv) < 4 or len(argv) > 5:
        raise ValueError(
            '''git_redline.py takes  either three or four arguments.\n
            Use python git_redline.py <path_to_redline_prefs.txt>
            <hash_from> <hash_to> <path_to_temporary_directory>''')
    path_to_redline_prefs = os.path.expanduser(argv[1])
    parse_redline_prefs = Prefs(path_to_redline_prefs)
    parse_hash_from = argv[2]
    parse_hash_to = argv[3]
    if len(argv) == 5:
        redline_prefs.path_to_temporary_directory = os.path.expanduser(argv[4])
    return parse_redline_prefs, parse_hash_from, parse_hash_to


if __name__ == '__main__':
    redline_prefs, hash_from, hash_to = parse_command_line(sys.argv)
    shutil.rmtree(
        redline_prefs.path_to_temporary_directory, ignore_errors=True)
    repo_from = Repo(redline_prefs, hash_from, 'from')
    repo_from.clone()
    repo_to = Repo(redline_prefs, hash_to, 'to')
    repo_to.clone()
    for flavor in redline_prefs.l_flavors:
        repo_from.generate_expanded_tex(flavor)
        repo_to.generate_expanded_tex(flavor)
        run_diff(repo_from, repo_to, flavor)
