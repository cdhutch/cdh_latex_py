#!/usr/bin/python3

import os
import re
import subprocess


def find_expand(path_to_mmd, path_to_texfile):
    print(path_to_texfile + '.tex')
    print(path_to_mmd)
    f_read = open(path_to_texfile + '.tex')
    for line in f_read:
        # print(line)
        m = re.match(test_input, line)
        if m is not None:
            input_code = re.sub(test_input, r'\1', line)[:-1]
            # print('**Begin ')
            # print(input_code)
            # print('******')
            f_write.write('% ' + line)
            f_write.write('% ***Begin: ' + input_code + '\n')
            file_seek = path_to_mmd + input_code
            print('Loading: ' + file_seek)
            try:
                find_expand(path_to_mmd, file_seek)
            except FileNotFoundError:
                find_expand(home_path + tex_directory, home_path + tex_directory + input_code)
            f_write.write('% ***End: ' + input_code + '\n')
            continue
        f_write.write(line)
    f_read.close()

#
# def find_inside(path_to_mmd, path_to_texfile):
#     print(path_to_texfile + '.tex')
#     # print(path_to_mmd)
#     f_read_inside = open(path_to_texfile + '.tex')
#     for line in f_read_inside:
#         # print(line)
#         m = re.match(test_input, line)
#         if m is not None:
#             input_code = re.sub(test_input, r'\1', line)[:-1]
#             # print('**Begin ')
#             # print(input_code)
#             # print('******')
#             f_write.write('% ' + line)
#             f_write.write('% ***Begin: ' + input_code + '\n')
#             file_seek = path_to_mmd + input_code
#             print('Loading: ' + file_seek)
#             # find_expand(path_to_mmd, file_seek)
#             f_write.write('% ***End: ' + input_code + '\n')
#             continue
#         f_write.write(line)
#     f_read_inside.close()

# home_path = '/Users/cdhutchi/Library/Application Support/Microsoft/Office/Lync/Dropbox/'
# home_path = '/Users/craig/Dropbox/'
icloud_drive_path = 'Library/Mobile Documents/com~apple~CloudDocs/'
home_path = '/Users/cdhutchi/'

# tex_filename = '20160805_conops'
# tex_filename = 'viewing_study_current_draft'
# tex_filename = '20161214_FSL Airbus Checklist'
tex_filename = 'Phase_1_Report'
tex_filename = 'cpf_conops'
# tex_directory = os.path.expanduser('SMAB/CLARREO/CONOPS/20160805_conops.txt/')
# tex_directory = os.path.expanduser('SMAB/CLARREO/STK Analysis/Viewing Study/viewing_study_current_draft.txt/')
# tex_directory = os.path.expanduser('Projects/Flight Sim LaTeX Checklists/')
tex_directory = os.path.expanduser('Documents/NASA/ISAAS/Reports/Local Sync/ISASS/Phase_1_Report.txt/')
tex_directory = os.path.expanduser('Documents/NASA/CLARREO/CONOPS/cpf_conops.txt/')
tex_mmd_directory = 'cdh_latex_config/tex/latex/peg-multimarkdown-latex-support-master/'

path_to_texfile = home_path + tex_directory + tex_filename
path_to_mmd = home_path + icloud_drive_path + tex_mmd_directory


test_input = re.compile(r'^\\input\{([-a-zA-Z_.0-9]+)\}$')
# test_input = re.compile(r'^\\input\{([-a-zA-Z_0-9]+)\}$')

f_write = open(path_to_texfile + '_expanded.tex', 'w')

find_expand(path_to_mmd, path_to_texfile)
f_write.close()

subprocess.run(["cp", path_to_texfile + '_expanded.tex', path_to_texfile + '_expanded_backup.tex'])
