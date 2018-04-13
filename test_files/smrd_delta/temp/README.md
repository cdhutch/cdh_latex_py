# cpf-smrd

Contains content files and code to generate CLARREO Pathfinder Science and Mission Requirements Document

To compile:

1. Export `.CSV` file from CORE into compile directory `<req_csv_fname>`
1. Compile Scrivener document to MMD into compile directory `<scriv_fname>`
1. Execute `build_smrd.py` script: `python build_smrd.py <scriv_fname> <req_csv_fname>`

## Auxiliary files

- `20170614_cprsp_cad.pdf`: CAD drawing of CPRSP with coordinate system and labels
- `20171214_cpf_architecture_l1-4.png`: CPF Mission Architecture to Level 4
- `nestedacros.tex`: TeX code for acronyms that tend to get nested; e.g. OTCM = ORU Tool Changeout Mechanism
- `mmd6-cpf-page-style.tex`: SMRD specific page styles to enable compile-time modification of revision and footer
- `revision_diff_summary.txt`: lists changes since previous revision
- `sed_acros.txt`: parameters used for full document text replacements using `sed`
- `sig_page.tex`: TeX document that contains information for SMRD Signature Page
- `CPF_SMRD_CR_docx`: Word file for FPD change request form
- `rev_hist.tex`: CLARREO Pathfinder SMRD Revision History and TBX Table Page for non-Supplemental document
- `rev_hist_supplemental.tex`: CLARREO Pathfinder SMRD Revision History and TBX Table Page for Supplemental document
- `poc_cpoc_icd.txt`: Text added to end of POIC Interface (GS.23000) requirement statement that enables trackable TBD
- `std_sci_data_products.txt`: Table added to Data Product Delivery (SCI.24000) requirement .

>>>>>>> cpf_smrd/master
