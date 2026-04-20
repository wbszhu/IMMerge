# IMMerge tests

Regression suite for IMMerge. Run with:

```bash
pip install -e .[dev]
pytest tests/
```

Verbose:

```bash
pytest tests/ -v
```

## What runs, and what skips

The suite is layered. Cheap checks run unconditionally; the expensive ones
skip gracefully when their environment is missing.

| Test group | What it covers | Skips when |
| --- | --- | --- |
| `TestPackage` | `import IMMerge`, version string, public API, version parity between `__init__` and `pyproject.toml` | never |
| `TestCliHelp` | `merge_files.py --help` and `make_info.py --help` exit 0 | never |
| `TestBfillRegression` | pandas 2.x `bfill` behaves the same as the deprecated `fillna(method='backfill')` that the code used to call | never |
| `TestGetSnpListRegression` | Running `get_snp_list` on `data_sample/` reproduces the golden info tables in `tests/fixtures/expected/` | `data_sample/` missing |
| `TestFullMergeEndToEnd` | Full `merge_files.py` pipeline reproduces the golden info tables and the merged VCF in `output_sample/merged_sample.vcf.gz` | no `bgzip` on PATH, or sample data missing |

## Golden fixtures

`tests/fixtures/expected/` contains the authoritative info tables the tests
diff against. These were generated from the current code on the sample
inputs in `data_sample/` and are the source of truth for info-table
format and content.

(`output_sample/` in the repo root may be stale — the committed copy was
produced with v0.0.3, which used a different column order and the old
`Rsq_groupN_cap_adj` column name.)

### Regenerating the golden info tables

If you change IMMerge in a way that intentionally alters info-table
output (column order, filtering logic, combined-stat math), regenerate
the golden and commit it:

```bash
python -c "
from pathlib import Path
from IMMerge.process_args import process_args
from IMMerge.get_SNP_list import get_snp_list

out = Path('tests/fixtures/expected/merged_sample')
flags = process_args([
    '--input',
    'data_sample/sample_group1.dose.vcf.gz',
    'data_sample/sample_group2.dose.vcf.gz',
    'data_sample/sample_group3.dose.vcf.gz',
    '--output', str(out),
    '--missing', '1',
    '--check_duplicate_id', 'True',
])
get_snp_list(flags)
"
rm -f tests/fixtures/expected/merged_sample.log  # non-deterministic
git add tests/fixtures/expected/
```

### Regenerating the reference VCF (`output_sample/merged_sample.vcf.gz`)

Needs `bgzip` installed. After any intentional change to merging
behavior, rerun the full pipeline and commit the new reference:

```bash
python src/IMMerge/merge_files.py \
    --input data_sample/sample_group1.dose.vcf.gz \
            data_sample/sample_group2.dose.vcf.gz \
            data_sample/sample_group3.dose.vcf.gz \
    --output output_sample/merged_sample \
    --check_duplicate_id true --missing 1
```

Note: `output_sample/` is currently `.gitignore`d in this fork. If you
want `TestFullMergeEndToEnd` to survive on fresh checkouts, remove that
line from `.gitignore` and commit both the regenerated outputs and the
`data_sample/` fixtures.

## Enabling the expensive tests

### Install `bgzip`

macOS:

```bash
brew install htslib
```

Debian / Ubuntu:

```bash
sudo apt install tabix
```

After install, `which bgzip` should print a path and
`TestFullMergeEndToEnd` will run.

### Restore `data_sample/` and `output_sample/`

Both directories are `.gitignore`d in this fork, so freshly-cloned
checkouts don't have them. Copy them from a previous checkout, or from
the upstream `belowlab/IMMerge` repo. Once present,
`TestGetSnpListRegression` will run.

## When a regression test fails

A failing diff in `TestGetSnpListRegression` or `TestFullMergeEndToEnd`
means one of two things:

1. **A regression** — recent code changes silently altered merge results.
   Investigate the diff and fix the bug.
2. **An intentional behavior change** — the golden is now stale.
   Regenerate it as described above and commit the update.

The tests print the first-diverging files; `diff <produced> <expected>`
from the shell will show you exactly what changed.
