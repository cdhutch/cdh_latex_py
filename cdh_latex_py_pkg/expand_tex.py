"""Parses and .tex file for \\input{} commands and expands into new document

Command Line Arguments:
    1. path_to_texfile: file to expand (required)
    2. path_to_tds: path to top of file structure to search for
        optional file (optional)

"""

import os
import re
import shutil
import sys


def file_seek(path_tds, input_code):
    for dirName, subdirList, fileList in os.walk(path_tds):
        for fname in fileList:
            if fname == input_code:
                return dirName, fname


def find_expand(path_to_tds, path_to_texfile, f_write, re_input, cwd):
    f_read = open(path_to_texfile)
    for line in f_read:
        m = re.match(re_input, line)
        if m is not None:
            input_code = re.sub(re_input, r'\1', line)
            f_write.write('% ' + line)
            f_write.write('% ***Begin: ' + input_code + '\n')
            try:
                tree_dir, input_fname = file_seek(
                    path_to_tds, input_code + '.tex')
            except TypeError:
                tree_dir, input_fname = file_seek(cwd, input_code + '.tex')
            input_fname_fullpath = os.path.join(tree_dir, input_fname)
            print(input_fname_fullpath)
            find_expand(
                path_to_tds, input_fname_fullpath, f_write, re_input, cwd)
            f_write.write('% ***End: ' + input_code + '\n')
            continue
        f_write.write(line)
    f_read.close()


def expand(argv):
    if len(argv) < 2 or len(argv) > 3:
        raise ValueError(
            '''expand_tex.py either one or two arguments.\n
            Use expand.py file.tex [path_to_texmf]''')
    path_to_texfile = os.path.expanduser(argv[1])
    cwd = os.path.dirname(os.path.abspath(path_to_texfile))
    path_to_tds = '~/Library/texmf'
    if len(argv) == 3:
        path_to_tds = argv[2]
    path_to_tds = os.path.expanduser(path_to_tds)
    f_write = open(path_to_texfile + '_expanded.tex', 'w')
    re_input = re.compile(r'^\\input{([-a-zA-Z_.0-9]+)}\n?$')
    find_expand(path_to_tds, path_to_texfile, f_write, re_input, cwd)
    f_write.close()
    shutil.copyfile(path_to_texfile + '_expanded.tex',
                    path_to_texfile + '_expanded_backup.tex')
    return path_to_texfile + '_expanded.tex'


def main(argv):
    return expand(argv)


if __name__ == '__main__':
    main(sys.argv)
