# cdh_latex_py

Go to root of repo and type `conda install .` to add to Python "path" in current conda environment. Package scripts:

- `compile_tex.py`
	- Compiles MD to PDF, via TeX and temporary directories
    - If run as routing, takes 1-2 command line arguments
        1. md_full_path: required
        2. temp_folder: optional
    - `TeX` class init:
        - md_full_path: path to source markdown file
        - temp_folder: temporary folder to use;
            defaults to ~/Documents/temporary/latex
        - compile_total: number of times to compile TeX code
        - in_fix: enables adding text within filenames
    - `prep_temp_directory()`: creates clean temporary directory;
        deletes any old copy
    - `apple_sed()`: runs sed command against file using external
        file with sed script
    - `compile_md()`: compiles MD to TeX
    - `compile_xetex()`: compiles TeX to PDF using XeLaTeX
- `expand_tex.py`
	- Parses and .tex file for \\input{} commands and expands into new document
	- Command Line Arguments:
	    1. path_to_texfile: file to expand (required)
	    2. path_to_tds: path to top of file structure to search for
	        optional file (optional)
- `git_redline.py`
	- Generates LaTeX document showing differences between two different versions of markdown documents posted on remote server
	- Command Line Arguments:
		1. path to redline preferences file
		2. commit hash of original document
		3. commit hash of updated document
		4. optional path to temporary directory (default: `~/Documents/temporary`)
	- Redline preferences file structure
		- Required
			- `url:` web address to remote repository
			- `repo_top`: folder of top level of repository
			- `repo_subdir`: path from `repo_top` to folder that holds document-specific compile script
			- `build_py`: filename of document compile script
			- `fname_md`: filename of markdown file to compile; determines name of output tex file
		- Optional
			- `branch`: branch to checkout after clone
			- `l_flavors`: A list of infixes for compilation, for example `['', 'supplemental']`
			- `repo_to_top`: `repo_top` folder specific to `to` repository
			- `repo_to_subdir`: `repo_subdir` folder specific to `to` repository
			- `build_to_py`: `build_py` folder specific to `to` repository
			- `repo_from_top`: `repo_top` folder specific to `from` repository
			- `repo_from_subdir`: `repo_subdir` folder specific to `from` repository
			- `build_from_py`: `build_py` folder specific to `from` repository
	- `Prefs()` class init:
		- path_to_redline_prefs: path to redline preferences files

	- `Repo()` class init:
		- repo_redline_prefs: object containing repo-specific preferences set from pref file
		- repo_hash: SHA1 code for remote commit
		- flag: "to" or "from"
