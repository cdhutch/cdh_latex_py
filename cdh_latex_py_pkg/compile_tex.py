""" Compiles MD to PDF, via TeX and temporary directories

    - If run as routing, takes 1-2 command line arguments
        1. md_full_path: required
        2. temp_folder: optional

    TeX class init:
        - md_full_path: path to source markdown file
        - temp_folder: temporary folder to use;
            defaults to ~/Documents/temporary/latex
        - compile_total: number of times to compile TeX code
        - in_fix: enables adding text within filenames

    - prep_temp_directory(): creates clean temporary directory;
        deletes any old copy
    - apple_sed(): runs sed command against file using external
        file with sed script
    - compile_md(): compiles MD to TeX
    - compile_xetex(): compiles TeX to PDF using XeLaTeX
"""
import shutil
import subprocess
import os
import re
import sys
import datetime


class TeX(object):
    def __init__(
            self, md_full_path=None, temp_folder=None,
            compile_total=3, in_fix=''):
        if md_full_path is None:
            if len(sys.argv) > 1:
                md_full_path = sys.argv[1]
        if temp_folder is None:
            if len(sys.argv) > 2:
                temp_folder = os.path.expanduser(sys.argv)
            else:
                temp_folder = os.path.expanduser(
                    '~/Documents/temporary/latex')
        self.temp_folder = temp_folder + in_fix
        self.cwd = os.path.dirname(
            os.path.abspath(os.path.expanduser(md_full_path)))
        root = os.path.splitext(os.path.basename(md_full_path))[0]
        self.root = root
        self.fname_md = root + '.txt'
        self.fname_tex = root + in_fix + '.tex'
        self.fname_sed = root + in_fix + '.sed'
        self.fname_pdf = root + in_fix + '.pdf'
        self.compile_total = compile_total
        self.in_fix = in_fix
        self.tbx_table_body = ''
        self.md_full_path = ''
        self.tex_full_path = ''

    @staticmethod
    def write_mmd_header(f, title, mmd_template='article'):
        f.write('latex config: {:s}\n'.format(mmd_template))
        f.write('Author:             Craig Hutchinson\n')
        f.write('Title:              ' + title + '  \n')
        f.write('Date:    ' +
                datetime.datetime.now().strftime('%d %B %Y') + '  \n')
        f.write('Base Header Level:  2  \n')

    def apply_sed(self, sed_file=None):
        tex_full_path = os.path.join(self.cwd, self.fname_tex)
        if sed_file is not None:
            subprocess.run(
                ['sed', '-E', '-i', 'bak', '-f', sed_file, tex_full_path])

    def compile_md(self):
        self.md_full_path = os.path.join(self.cwd, self.fname_md)
        self.tex_full_path = os.path.join(self.cwd, self.fname_tex)
        subprocess.run(['multimarkdown', '-t', 'latex',
                        '-o', self.tex_full_path, self.md_full_path])

    def compile_xetex(self):
        self.tex_full_path = os.path.join(self.cwd, self.fname_tex)
        for i in range(self.compile_total):
            subprocess.run(
                ['xelatex', '-interaction=batchmode', self.tex_full_path])
        l_aux_ext = ['acn', 'acr', 'alg', 'aux', 'glg', 'glo', 'gls',
                     'glsdefs', 'idx', 'ist', 'lof', 'log', 'lot',
                     'bak', 'old', 'out', 'toc', 'texbak', 'tex.old',
                     'sedbak']
        for aux_ext in l_aux_ext:
            fname_aux = self.root + self.in_fix + '.' + aux_ext
            try:
                shutil.move(os.path.join(self.cwd, fname_aux),
                            os.path.join(self.temp_folder, fname_aux))
            except FileNotFoundError:
                print(fname_aux)
                pass

    def prep_temp_directory(self):
        shutil.rmtree(self.temp_folder, ignore_errors=True)
        os.makedirs(self.temp_folder, exist_ok=True)

    def pass1(self, thicklines=False):
        re_tbx = re.compile(r'\\Q?TB([RD])\{([^\}]*)\}')
        re_qtbx = re.compile(r'\\QTB[RD]')
        re_glossary = re.compile(
            r'\\longnewglossaryentry{(\w+([-\s]+\w+)+)}')
        l_glossary = []
        fpath_fname_old = self.tex_full_path + '.old'
        subprocess.run(["mv", self.tex_full_path, fpath_fname_old])
        print('Reading in: ' + fpath_fname_old)
        f_read = open(fpath_fname_old, 'r')
        f_write = open(self.tex_full_path, 'w')
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
            line = re.sub(r'\\toprule', r'\\hline', line)
            line = re.sub(r'\\bottomrule', r'\\hline', line)
            line = re.sub(r'\\midrule', r'\\hline', line)
            # Seek TBR/TBD codes
            m = re.search(re_tbx, line)
            while m is not None:
                tbx_num_label = 'tbx_' + '{:d}'.format(tbx_num)
                mm = re.search(re_qtbx, line)
                if mm is not None:
                    tbx_label = r'\\label{' + tbx_num_label + '}'
                else:
                    tbx_label = 'TB' + m.group(1) +\
                        r'\\label{' + tbx_num_label + '}'
                line_new = re.sub(re_tbx, tbx_label, line)
                # print(line_new)
                line = line_new
                tbx_table_body += 'TB' + m.group(1) + ' & ' +\
                                  m.group(2) + r' & \pageref{' + \
                    tbx_num_label + '}  \\\\ \n \\hline \n'
                tbx_num += 1
                m = re.search(re_tbx, line)
            # Build multi word glossary list
            m = re.search(re_glossary, line)
            if m is None:
                for glossary in l_glossary:
                    if glossary in line:
                        print('I found ' + glossary)
                        line = line.split(glossary)[
                            0] + r'\gls{' + glossary + '}' +\
                            line.split(glossary)[1]
                        l_glossary.remove(glossary)
                        print(line)
            else:
                print('I added ' + m.group(1))
                l_glossary += [m.group(1)]
                print(l_glossary)
            f_write.write(line)
            m = None
            if m is None:
                pass
        print('Writing out: ' + self.tex_full_path)
        print(l_glossary)
        f_write.close()
        return tbx_table_body

    def pass2(self):
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
            \small
            \begin{tabular}
            {| >{\centering\arraybackslash}m{1.25in}|
            >{\centering\arraybackslash}m{2.95in}|
            >{\centering\arraybackslash}m{1.5in}|}
            \hline
            \bfseries{Item} & \bfseries{Description} & \bfseries{Page}\\
            \hline
            '''

        tbx_table_end = r'''\end{tabular}
        \end{minipage}
        \end{table}
        \raggedright
        \clearpage'''

        f_write = open('tbx_table.tex', 'w')
        f_write.write(tbx_table_start + self.tbx_table_body + tbx_table_end)
        f_write.close()


def main():
    tex_file = TeX()
    tex_file.prep_temp_directory()
    tex_file.compile_md()
    tex_file.apply_sed()
    tex_file.compile_xetex()


def test_code():
    md_fname = '~/Documents/GitHub/cdh_latex_py'
    md_fname += '/test_files/A2A C172 Checklist_mmd6.txt'
    tex_file = TeX(md_fname)
    tex_file.prep_temp_directory()
    tex_file.compile_md()
    tex_file.apply_sed()
    tex_file.compile_xetex()


if __name__ == '__main__':
    main()
