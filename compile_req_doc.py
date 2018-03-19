#!/usr/bin/python3

import os
# import pandas as pd
import subprocess
import sys
import datetime
import time
import shutil
import compile_tex


class RequirementDoc(object):
    def __init__(self, scriv_fname, csv_fname, rs, temp_dir=None,
                 d_supplemental_files=None, d_unique_headings=None):
        self.scriv_fname = scriv_fname
        if temp_dir is None:
            rs.temp_dir = os.path.expanduser(
                '~/Documents/temporary/reqs_compile')
        else:
            rs.temp_dir = os.path.expanduser(temp_dir)
        rs.csv_fname = csv_fname
        if d_supplemental_files is None:
            rs.d_supplemental_files = dict()
        else:
            rs.d_supplemental_files = d_supplemental_files
        if d_unique_headings is None:
            rs.d_unique_headings = dict()
        else:
            rs.d_unique_headings = d_unique_headings
        pass

    def pre_compile(self, rs):
        # start_dir = os.getcwd()
        # rs = RequirementSet()
        # rs.csv_fname = sys.argv[2]
        # rs.temp_dir = os.path.expanduser('~/Documents/temporary/cpf-smrd-compile/')
        # rs.temp_dir = self.temp_dir
        # rs.d_supplemental_files = {'SCI.24000': 'std_sci_data_products.txt',
        #                            'GS.23000': 'poc_cpoc_icd.txt'}
        # rs.d_unique_headings = {
        #     '4.2.1': '\n## Mission Requirements  \n',
        #     '4.2.2.1': '\n### Science Segment Requirements  \n'}
        rs.prep_temp_directory()
        rs.req_md_fname = rs.csv_fname.split('.')[0] + '_reqs.txt'
        rs.load_rs()
        rs.write_reqs()
        shutil.copy(
            'mmd6-cpf-page-styles_source.tex', 'mmd6-cpf-page-styles.tex')
        s_mod_date = datetime.datetime.strptime(
            time.ctime(os.path.getmtime(
                rs.csv_fname)), "%a %b %d %H:%M:%S %Y").strftime(
                    "%d %B %Y").lstrip('0')
        s_footer = 'The electronic version is the official approved document.'
        s_sed = r's/' + s_footer + r'/' + s_footer + \
            r'\\\\The requirements are from a CORE database query dated: ' +\
            s_mod_date + r'./'
        subprocess.run(['sed', '-E', '-i', '', s_sed,
                        'mmd6-cpf-page-styles.tex'])

    def compile(self, rs, l_infix):
        # scriv_fname = sys.argv[1]
        for infix in l_infix:
            version_md_full_path = os.path.abspath(
                os.path.expanduser(
                    self.scriv_fname))
            req_doc_tex = compile_tex.TeX(
                version_md_full_path, rs.temp_dir, in_fix=infix)
            req_doc_tex.prep_temp_directory()
            os.chdir(req_doc_tex.cwd)
            fname_reqs_md = os.path.join(
                req_doc_tex.cwd, rs.req_md_fname.split('.')[0] + infix + '.txt')
            shutil.copy(fname_reqs_md, os.path.join(
                req_doc_tex.cwd, 'reqs_compile.txt'))
            shutil.copy('rev_hist' + infix + '.tex', 'rev_hist_compile.tex')
            req_doc_tex.compile_md()
            req_doc_tex.apply_sed('sed_acros.txt')
            req_doc_tex.tex_full_path = os.path.join(
                req_doc_tex.cwd, req_doc_tex.fname_tex)
            if len(sys.argv) < 4:
                req_doc_tex.tbx_table_body = req_doc_tex.pass1()
            if req_doc_tex.tbx_table_body is not None:
                req_doc_tex.pass2()
            s_rev = infix[1:].title() + ' '
            f_sed = open('sed_rev.txt', 'w')
            s_sed = r's/\\def\\revision{(.*)}/\\def\\revision{\1 ' + \
                s_rev + r'}/'
            f_sed.write(s_sed)
            f_sed.close()
            subprocess.run(['sed', '-E', '-i', '', '-f',
                            'sed_rev.txt', req_doc_tex.tex_full_path])
            req_doc_tex.compile_xetex()
            l_compile_files = [
                'reqs_compile.txt', 'rev_hist_compile.tex', 'sed_rev.txt',
                'tbx_table.tex']
            for compile_file in l_compile_files:
                try:
                    shutil.move(compile_file, req_doc_tex.temp_folder)
                except FileNotFoundError:
                    pass
        try:
            shutil.move('mmd6-cpf-page-styles.tex', req_doc_tex.temp_folder)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    pass
