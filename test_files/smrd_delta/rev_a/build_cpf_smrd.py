#!/usr/bin/python3

import os
import pandas as pd
import re
import subprocess
import sys
import datetime
import time


class RequirementSet(object):
    def __init__(self):
        self.row_old = pd.DataFrame({'Number': ['Garfield']}).iloc[0]

    def load_rs(self):
        self.df = pd.read_csv(self.csv_fname, encoding="ISO-8859-1")

    def write_reqs(self):
        s_fname = self.md_fname.split(".")
        f_contract = open(
            s_fname[0] + '.' + s_fname[1], 'w')
        f_supplemental = open(
            s_fname[0] + '_supplemental.' + s_fname[1], 'w')
        l_sec_num = self.df['Reported by Number'].dropna().unique()
        l_sec_num.sort()
        for sec_num in l_sec_num:
            df_sec = self.df[(self.df['Reported by Number'] == sec_num)]
            sec_str = ''
            if sec_num in self.d_unique_headings:
                sec_str = self.d_unique_headings[sec_num]
            sec_str += '#' * len(sec_num.split('.'))
            sec_str += ' ' + df_sec['Reported by Title'].iloc[0] + '  \n'
            f_contract.write(sec_str)
            f_supplemental.write(sec_str)

            for index, row in df_sec.iterrows():
                req_str = ''
                if self.row_old['Number'] != row['Number']:
                    req_str = '\n**[' + row['Number'] + ']** ' + \
                        row['Title'] + '  \n\n'
                    req_str += row['Requirement Text'] + '  \n\n'
                    f_contract.write(req_str)
                    f_supplemental.write(req_str)
                    req_str = '- Rationale: *' + \
                        str(row['Rationale']) + '*  \n'
                    f_supplemental.write(req_str)
                req_str = '- Verification Method: ' + \
                    str(row['Verification Method']) + '  \n'
                req_str += '- Verification Description: ' + \
                    str(row['Verification Description']) + '  \n'
                req_str += '- Success Criteria: ' + \
                    str(row['Success Criteria']) + '  \n'
                f_supplemental.write(req_str)
                req_str = ''
                if row['Number'] in self.d_supplemental_files:
                    req_str += '\n\n'
                    req_str +=\
                        '{{' + self.d_supplemental_files[row['Number']] + '}}'
                    req_str += '\n\n'
                f_contract.write(req_str)
                f_supplemental.write(req_str)
                self.row_old = row
        f_contract.close()
        f_supplemental.close()


def pass1(fpath_fname, thicklines=False):
    re_tbx = re.compile(r'\\Q?TB([RD])\{([^\}]*)\}')
    re_qtbx = re.compile(r'\\QTB[RD]')
    fpath_fname_old = fpath_fname + '.old'
    subprocess.run(["mv", fpath_fname, fpath_fname_old])
    print('Reading in: ' + fpath_fname_old)
    f_read = open(fpath_fname_old, 'r')
    f_write = open(fpath_fname, 'w')
    re_tabulary = re.compile(r'\\begin\{tabulary\}\{(\S*)\}\{(\S*)\}')
    re_tablewidth = re.compile(r'\\tablewidth\{([\S]*)\}')
    column_format = None
    next_line_table_header = False
    tbx_num = 1
    tbx_table_body = ''
    for line in f_read:
        # Bold face first line of table
        if next_line_table_header is True:
            f_write.write(r'\rowstyle{\bfseries}%')
            f_write.write('\n')
            next_line_table_header = False
        # Set column format to text line having \tablewidth code
        if re.search(re_tablewidth, line) is not None:
            column_format = re.sub(re_tablewidth, r'\1', line)[:-2]
            line = ''
        # Replace preamble with column format in tabulary environment
        if re.search(re_tabulary, line) is not None:
            if column_format is not None:
                str_tab_replace = r'\\begin{tabulary}{\1}{' + \
                    column_format + '}'
                line = re.sub(re_tabulary, str_tab_replace, line)
                column_format = None
            next_line_table_header = True
        # Replace toprule, bottomrule, midrule with hline
        # to allow vertical lines in tables
        line = re.sub(r'\\toprule', '\hline', line)
        line = re.sub(r'\\bottomrule', '\hline', line)
        line = re.sub(r'\\midrule', '\hline', line)
        # Seek TBR/TBD codes
        m = re.search(re_tbx, line)
        while m is not None:
            tbx_num_label = 'tbx_' + '{:d}'.format(tbx_num)
            mm = re.search(re_qtbx, line)
            if mm is not None:
                tbx_label = '\label{' + tbx_num_label + '}'
            else:
                tbx_label = 'TB' + m.group(1) + '\label{' + tbx_num_label + '}'
            line_new = re.sub(re_tbx, tbx_label, line)
            print(line_new)
            line = line_new
            tbx_table_body += 'TB' + m.group(1) + ' & ' +\
                              m.group(2) + ' & \pageref{' + \
                tbx_num_label + '}  \\\\ \n \\hline \n'
            tbx_num += 1
            m = re.search(re_tbx, line)
        f_write.write(line)
    print('Writing out: ' + fpath_fname)
    f_write.close()
    return tbx_table_body


def pass2(fpath_fname, tbx_table_body):
    tbx_table_start = r'''
        \clearpage
        \sffamily
        \bfseries
        \center{\large TBX LIST\par}
        \normalfont
        \centering
        \begin{table}[htbp]
        \begin{minipage}{\linewidth}
        \setlength{\tymax}{0.5\linewidth}
        \centering
        \small\begin{tabular}{| >{\centering\arraybackslash}m{1.25in}| >{\centering\arraybackslash}m{2.95in}| >{\centering\arraybackslash}m{1.5in}|} \hline
        \bfseries{Item} & \bfseries{Description} & \bfseries{Page}\\
        \hline
        '''

    tbx_table_end = r'''\end{tabular}
    \end{minipage}
    \end{table}
    \raggedright
    \clearpage'''

    f_write = open('tbx_table.tex', 'w')

    f_write.write(tbx_table_start + tbx_table_body + tbx_table_end)
    f_write.close()


def fix_acronyms(fpath_fname, thicklines=False):
    subprocess.run(['sed', '-E', '-i', 'bak', '-f', 'sed.txt', fpath_fname])


scriv_fname = sys.argv[1]
rs = RequirementSet()
rs.csv_fname = sys.argv[2]
rs.d_supplemental_files = {'SCI.24000': 'std_sci_data_products.txt',
                           'GS.23000': 'poc_cpoc_icd.txt'}
rs.d_unique_headings = {'4.2.1': '\n## Mission Requirements  \n',
                        '4.2.2.1': '\n### Science Segment Requirements  \n'}
rs.md_fname = rs.csv_fname.split('.')[0] + '_reqs.txt'
rs.load_rs()
rs.write_reqs()
subprocess.run(['cp', 'mmd6-cpf-page-styles_source.tex',
                'mmd6-cpf-page-styles.tex'])
s_mod_date = datetime.datetime.strptime(time.ctime(os.path.getmtime(
    rs.csv_fname)), "%a %b %d %H:%M:%S %Y").strftime("%d %B %Y").lstrip('0')
s_footer = 'The electronic version is the official approved document.'
s_sed = r's/' + s_footer + r'/' + s_footer + \
    r'\\\\The requirements are from a CORE database query dated: ' +\
    s_mod_date + r'./'
print(s_sed)
subprocess.run(['sed', '-E', '-i', '', s_sed, 'mmd6-cpf-page-styles.tex'])
for smrd in ['', '_supplemental']:
    subprocess.run(['cp', rs.md_fname.split(
        '.')[0] + smrd + '.txt', 'reqs_compile.txt'])
    subprocess.run(['cp', 'rev_hist' + smrd + '.tex', 'rev_hist_compile.tex'])
    tex_fname = scriv_fname.split('.')[0] + smrd + '.tex'
    subprocess.run(['multimarkdown', '-t', 'latex',
                    '-o', tex_fname, scriv_fname])
    fix_acronyms(tex_fname)
    if len(sys.argv) < 4:
        tbx_table_body = pass1(tex_fname)
    if tbx_table_body is not None:
        pass2(tex_fname, tbx_table_body)
    # Update Document Version for each tex file
    s_rev = smrd[1:].title() + ' '
    f_sed = open('sed_rev.txt', 'w')
    s_sed = r's/\\def\\revision{(.*)}/\\def\\revision{\1 ' + \
        s_rev + r'}/'
    f_sed.write(s_sed)
    f_sed.close()
    subprocess.run(['sed', '-E', '-i', '', '-f',
                    'sed_rev.txt', tex_fname])
    # Compile TeX to PDF 3 times to ensure completeness
    for i in range(3):
        subprocess.run(['xelatex', '-interaction=batchmode', tex_fname])
