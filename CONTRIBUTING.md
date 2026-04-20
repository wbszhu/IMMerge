# Contributing to IMMerge

Thanks for taking the time to contribute. This file describes how to report
bugs, suggest enhancements, and submit pull requests.

## Reporting bugs

Please open an issue with:

- IMMerge version: `python -c "import IMMerge; print(IMMerge.__version__)"`
- Python version, pandas version, and OS
- The exact command you ran (with flags)
- The full error message / traceback
- A minimal input that reproduces the issue, if possible

## Suggesting features

Open an issue describing the use case, the proposed behavior, and any
alternatives you considered.

## Development setup

```bash
git clone https://github.com/wbszhu/IMMerge
cd IMMerge
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then verify the install:

```bash
python -c "import IMMerge; print(IMMerge.__version__)"
```

You also need the external `bgzip` tool (from
[htslib](https://github.com/samtools/htslib)) on your `PATH` for the merging
step to succeed.

## Running the sample workflow

The `data_sample/` and `output_sample/` directories contain a small end-to-end
example. After any change, rerun the sample merge and diff the outputs
against `output_sample/` to check that behavior is preserved:

```bash
python src/IMMerge/merge_files.py \
    --input data_sample/sample_group1.dose.vcf.gz \
            data_sample/sample_group2.dose.vcf.gz \
            data_sample/sample_group3.dose.vcf.gz \
    --output /tmp/test_merged \
    --check_duplicate_id true --missing 1
```

## Pull requests

- One focused change per PR.
- Preserve existing CLI flags, defaults, and output file formats — external
  users depend on them. If you must change behavior, call it out explicitly in
  the PR body and bump the minor version.
- Describe *what* and *why* in the PR body, not just the diff.
- Add an entry to `CHANGELOG.md` under an `## [Unreleased]` heading.
