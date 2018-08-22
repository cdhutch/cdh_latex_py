''' Takes paths to two LaTeX files, expands them as necessary, computes diff, then compiles

    Syntax: latex_diff.py <path_to_old_file> <path_to_new_file> <path_to_temporary_directory>
    Result is diff.pdf file in <path_to_temporary_directory>
'''


import sys
import os
import expand_tex
import shutil
import subprocess


def get_filepaths(args):
    if len(args) != 4:
        error_string = "latex_diff requires exactly 3 argumets\n"
        error_string += "python latex_diff <path_to_old_file> "
        error_string += "<path_to_new_file> <path_to_temporary_directory>\n"
        raise ValueError(error_string)
    old_path = os.path.abspath(os.path.expanduser(args[1]))
    new_path = os.path.abspath(os.path.expanduser(args[2]))
    temp_path = os.path.abspath(os.path.expanduser(args[3]))
    return old_path, new_path, temp_path


def populate_temp_dir(old_path, new_path, temp_path, preserve_diff):
    if preserve_diff is False:
        shutil.rmtree(temp_path, ignore_errors=True)
    shutil.copytree(os.path.dirname(new_path), temp_path)
    l_expand_tex = []
    for label, path in [('old', old_path), ('new', new_path)]:
        tex = expand_tex.expand([0, path])
        split = os.path.splitext(os.path.basename(tex))
        temp_tex = split[0] + '_' + label + split[1]
        shutil.move(tex, os.path.join(temp_path, temp_tex))
        l_expand_tex.append(temp_tex)
    return l_expand_tex


def run_latexdiff(l_expand_tex, temp_path, hash_from, hash_to, flavor):
    hashtext = '_' + hash_from + '-' + hash_to
    if hashtext == '_-':
        hashtext = ''
    fname_diff = l_expand_tex[0].split('.')[0] + '_diff' + hashtext + '.tex'
    cmd = 'latexdiff '
    cmd += os.path.join(temp_path, l_expand_tex[0])
    cmd += ' '
    cmd += os.path.join(temp_path, l_expand_tex[1])
    cmd += ' > '
    diff_tex = os.path.join(temp_path, (fname_diff))
    cmd += diff_tex
    p = subprocess.Popen(cmd, shell=True)
    os.waitpid(p.pid, 0)
    return diff_tex


def compile_diff(diff_tex):
    os.chdir(os.path.dirname(diff_tex))
    for i in range(3):
        subprocess.run(
            ['xelatex', '-interaction=batchmode', diff_tex])


def main(argv, hash_from='', hash_to='', flavor='', preserve_diff=False):
    # get filesnames of old and new file
    old_path, new_path, temp_path = get_filepaths(argv)
    # expands tex files to temporary directory
    l_expand_tex = populate_temp_dir(old_path, new_path, temp_path, preserve_diff)
    # run latexdiff
    diff_tex = run_latexdiff(
        l_expand_tex, temp_path, hash_from, hash_to, flavor)
    # compile results
    compile_diff(diff_tex)
    print('Run complete')


if __name__ == '__main__':
    main(sys.argv)
    # # get filesnames of old and new file
    # old_path, new_path, temp_path = get_filepaths(sys.argv)
    # # expands tex files to temporary directory
    # l_expand_tex = populate_temp_dir(old_path, new_path, temp_path)
    # # run latexdiff
    # diff_tex = run_latexdiff(l_expand_tex, temp_path)
    # # compile results
    # compile_diff(diff_tex)
    # print('Run complete')
