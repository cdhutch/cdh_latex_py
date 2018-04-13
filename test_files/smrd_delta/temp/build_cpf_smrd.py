#!/usr/bin/python3

import pandas as pd
import sys
import compile_req_doc


class RequirementSet(object):
    def __init__(self):
        self.row_old = pd.DataFrame({'Number': ['Garfield']}).iloc[0]

    def load_rs(self):
        def _parent_req(row):
            if pd.isnull(row['PLRA_number']):
                val = row['local_parent_number']
            else:
                val = row['PLRA_number']
            return val

        self.df = pd.read_csv(self.csv_fname, encoding="ISO-8859-1")
        self.df['parent_req'] = self.df.apply(_parent_req, axis=1)

    def write_reqs(self):
        s_fname = self.req_md_fname.split(".")
        f_contract = open(
            self.temp_dir + s_fname[0] + '.' + s_fname[1], 'w')
        f_supplemental = open(
            self.temp_dir + s_fname[0] + '_supplemental.' + s_fname[1], 'w')
        l_sec_num = self.df['Reported by Number'].dropna().unique()
        l_sec_num.sort()
        for sec_num in l_sec_num:
            df_sec = self.df[(self.df['Reported by Number'] == sec_num)].drop(
                ['PLRA_number', 'local_parent_number', 'parent_req'],
                axis=1).drop_duplicates()
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
                    req_str += '- Parent Requirements: '
                    df_kid = self.df[(self.df['Number'] == row['Number'])][[
                        'Number', 'parent_req']].drop_duplicates()
                    # int_kid = df_kid.shape[0]
                    for kid_index, kid_row in df_kid.iterrows():
                        req_str += kid_row['parent_req'] + ', '
                        # if kid_index < int_kid - 1:
                        #     req_str += ', '
                    req_str = req_str[:-2] + '\n'
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


if __name__ == '__main__':
    rs = RequirementSet()
    temp_dir = '~/Documents/temporary/cpf-smrd-compile/'
    d_supplemental_files = {'SCI.24000': 'std_sci_data_products.txt',
                            'GS.23000': 'poc_cpoc_icd.txt'}
    d_unique_headings = {
        '4.2.1': '\n## Mission Requirements  \n',
        '4.2.2.1': '\n### Science Segment Requirements  \n'}
    req_doc = compile_req_doc.RequirementDoc(
        sys.argv[1], sys.argv[2], rs, temp_dir=temp_dir,
        d_supplemental_files=d_supplemental_files,
        d_unique_headings=d_unique_headings)
    req_doc.pre_compile(rs)
    l_infix = ['', '_supplemental']
    req_doc.compile(rs, l_infix)
