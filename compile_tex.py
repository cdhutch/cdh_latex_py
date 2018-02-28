""" Compiles MD to PDF, via TeX and temporary directories

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


class TeX(object):
    def __init__(
            self, md_full_path, temp_folder=None, compile_total=3, in_fix=''):
        if temp_folder is None:
            self.temp_folder = os.path.expanduser(
                '~/Documents/temporary/latex')
        else:
            self.temp_folder = temp_folder
        # cwd = os.path.abspath(os.path.dirname(md_full_path))
        self.cwd = os.path.abspath(os.path.dirname(md_full_path))
        root = os.path.splitext(os.path.basename(md_full_path))[0]
        self.md_fname = root + '.txt'
        self.tex_fname = root + '.tex'
        self.pdf_fname = root + '.pdf'
        self.compile_total = compile_total

    def compile_md(self):
        md_full_path = os.path.join(self.cwd, self.md_fname)
        tex_full_path = os.path.join(self.temp_folder, self.tex_fname)
        subprocess.run(['multimarkdown', '-t', 'latex',
                        '-o', tex_full_path, md_full_path])
        shutil.copy(tex_full_path, self.cwd)

    def compile_xetex(self):
        os.chdir(self.temp_folder)
        tex_full_path = os.path.join(self.temp_folder, self.tex_fname)
        pdf_full_path = os.path.join(self.temp_folder, self.pdf_fname)
        for i in range(self.compile_total):
            subprocess.run(
                ['xelatex', '-interaction=batchmode', tex_full_path])
        shutil.copy(pdf_full_path, self.cwd)
        pass

    def prep_temp_directory(self):
        shutil.rmtree(self.temp_folder, ignore_errors=True)
        os.makedirs(self.temp_folder, exist_ok=True)


def main():
    pass


def test_code():
    tex_file = TeX(
        '~/Documents/GitHub/cdh_latex_py/test_files/A2A C172 Checklist_mmd6.txt'
    )
    tex_file.prep_temp_directory()
    tex_file.compile_md()
    tex_file.compile_xetex()


if __name__ == '__main__':
    main()
    test_code()
