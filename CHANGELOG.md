# Changelog

All notable changes to this project are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and the format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.0.5] - 2026-04-20

### Changed
- Slim README to a landing-page format (install, quickstart, output
  files, docs pointer, citation, license). Full CLI reference,
  input-file format, and Python module API moved to `docs/usage.md`.
  Combined R² / MAF / AF derivations moved to `docs/algorithm.md`.
  New `docs/README.md` indexes the manual.

### Added
- `pyproject.toml` for PEP 517/621 packaging — installable with `pip install .`.
- `requirements.txt` for environments that need a flat dependency list.
- `CITATION.cff` so GitHub can render a "Cite this repository" widget and export
  BibTeX/APA automatically.
- `CONTRIBUTING.md` with bug-reporting, dev-setup, and PR guidelines.
- `.github/ISSUE_TEMPLATE/` with bug report and feature request templates.
- `.github/PULL_REQUEST_TEMPLATE.md` reminding contributors not to break CLI/output format.
- README restructure: Table of Contents, badges (License / Python / PyPI / DOI),
  a new "Output Files" section describing each artifact, and language hints on all
  fenced code blocks.
- Single source of truth for `__version__` in `src/IMMerge/merge_files.py`,
  re-exported from the package root (`IMMerge.__version__`).

### Fixed
- **pandas 2.x compatibility**: replaced deprecated
  `fillna(method='backfill', axis=1)` with `.bfill(axis=1)` in
  `src/IMMerge/get_SNP_list.py`. The previous form would raise `TypeError` on
  pandas ≥ 2.0.
- Typos in source comments and a dead-code function name (no runtime behavior change):
  `Patameters` → `Parameters`, `stoo` → `too`, `progres` → `progress`,
  `check_imputatilson_parameters` → `check_imputation_parameters`.
- Typos in README: `TOMed` → `TOPMed`, `at leat` → `at least`, `fo reach` → `for each`.
- Python example blocks in README were fenced as ` ```bash ` instead of ` ```python `.

## [0.0.4]

- Fix SNP sorting bug in `get_SNP_list.py`: preserve original VCF row order for
  multiallelic positions by sorting on input index columns instead of the SNP ID.
- Allow user-supplied retained SNP list (`--retained_snp_list`).

## [0.0.3]

- Fix multiallelic handling error in `get_SNP_list.py`.
- Add `ALL/SOME/NONE` mixed genotype status: `--mixed_genotype_status`,
  `--imputed_label`, `--genotyped_label`.
- `merge_files.py`: improved error message when a SNP is not found at end of file.

## [0.0.2]

- `make_info.py` now handles INFO rows with differently ordered fields.

## [0.0.1]

- Initial release corresponding to the Bioinformatics 2023 publication
  (DOI: 10.1093/bioinformatics/btac750).
