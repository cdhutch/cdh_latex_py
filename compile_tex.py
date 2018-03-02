""" Compiles MD to PDF, via TeX and temporary directories

    - If run as routing, takes 1-2 command line arguments
        1. md_full_path: required
        2. temp_foplder: optional

    TeX class init:
        - md_full_path: path to source markdown file
        - temp_folder: temporary folder to use;
            defaults to ~/Documents/temporary/latex
        - compile_total: number of times to compile TeX code
        - in_fix: future feature

    - compile_md(): compiles MD to TeX
    - compile_xetex(): compilex TeX to PDF using XeLaTeX
    - prep_temp_directory(): creates clean temporary directory;
        deletes any old copy

"""
import shutil
import subprocess
import os
import sys


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

    def apply_sed(self, sed_file=None):
        tex_full_path = os.path.join(self.cwd, self.fname_tex)
        if sed_file is not None:
            subprocess.run(
                ['sed', '-E', '-i', 'bak', '-f', sed_file, tex_full_path])

    def compile_md(self):
        md_full_path = os.path.join(self.cwd, self.fname_md)
        tex_full_path = os.path.join(self.cwd, self.fname_tex)
        subprocess.run(['multimarkdown', '-t', 'latex',
                        '-o', tex_full_path, md_full_path])

    def compile_xetex(self):

        tex_full_path = os.path.join(self.cwd, self.fname_tex)
        for i in range(self.compile_total):
            subprocess.run(
                ['xelatex', '-interaction=batchmode', tex_full_path])
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
                pass

    def prep_temp_directory(self):
        shutil.rmtree(self.temp_folder, ignore_errors=True)
        os.makedirs(self.temp_folder, exist_ok=True)


def main():
    tex_file = TeX()
    tex_file.prep_temp_directory()
    tex_file.compile_md()
    tex_file.apply_sed()
    tex_file.compile_xetex()


def test_code():
    tex_file = TeX(
        '~/Documents/GitHub/cdh_latex_py/test_files/A2A C172 Checklist_mmd6.txt'
    )
    tex_file.prep_temp_directory()
    tex_file.compile_md()
    tex_file.apply_sed()
    tex_file.compile_xetex()


if __name__ == '__main__':
    main()
