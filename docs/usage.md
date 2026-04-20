# IMMerge Usage Guide

Full reference for `merge_files.py` and `make_info.py`, including input file
requirements, output files, and the Python module API.

For installation and a one-command quick start, see the
[project README](../README.md).

## Contents

- [Input files](#input-files)
- [File format notes](#file-format-notes)
- [merge_files.py — CLI reference](#merge_filespy--cli-reference)
- [make_info.py — CLI reference](#make_infopy--cli-reference)
- [Examples](#examples)
- [Python module API](#python-module-api)

---

## Input files

IMMerge reads two files per cohort:

1. A bgzip-compressed, position-sorted VCF (`*.vcf.gz`) — typically the
   output of an imputation server such as TOPMed.
2. A matching compressed info table (`*.info.gz`) placed in the same
   directory, with the same basename as the VCF. Use `make_info.py` to
   generate these from a VCF if you do not already have them.

The info file must contain the following columns (extra columns are
ignored):

| SNP                | REF(0) | ALT(1) | ALT_Frq | MAF     | Rsq     | Genotyped |
| ------------------ | ------ | ------ | ------- | ------- | ------- | --------- |
| chr21:10000777:C:A | C      | A      | 0.00003 | 0.00003 | 0.44840 | IMPUTED   |
| chr21:10000931:T:G | T      | G      | 0.00004 | 0.00004 | 0.46070 | TYPED     |
| chr21:10001844:A:G | A      | G      | 0.00002 | 0.00002 | 0.65686 | IMPUTED   |
| chr21:10001985:C:T | C      | T      | 0.00001 | 0.00001 | 0.18849 | IMPUTED   |

`SNP`, `REF(0)`, `ALT(1)`, `ALT_Frq`, `MAF`, `Rsq`, and `Genotyped` are
required.

## File format notes

1. All input files should be compressed (gzip or bgzip); the format
   should follow post-imputation VCF from TOPMed.
2. Variants must be sorted by position (TOPMed output already is).
3. Info files must sit next to their VCFs as `[file_name].info.gz`
   unless you override with `--info`.
4. If your VCFs do not have matching `.info.gz` files, generate them
   with `make_info.py`. Input VCFs must have at least these four fields
   in the `INFO` column: `AF`, `MAF`, imputation quality (e.g. `R2`),
   and genotype status (e.g. `IMPUTED`/`TYPED`/`TYPED_ONLY`).
5. Do not move or modify `variants_retained.info.txt` or
   `variants_excluded.info.txt` while a run is in progress.
6. Output files are overwritten without warning if a subsequent run
   targets the same `--output` prefix.
7. Values smaller than 0.000001 (six digits of precision) are rounded
   to 0 when writing `ALT_Frq`, `MAF`, and `R2` into the retained /
   excluded info tables, and when rewriting the VCF `INFO` column.
   Precision is controlled by `float_format` in `get_SNP_list.py`.

---

## merge_files.py — CLI reference

- `--input`: (Required) files to be merged, multiple files are allowed.
- `--info`: (Optional) Directory/name to info files. Default path is the
  same directory as corresponding input file; default info file shares
  the same name as input file except for suffix (`.info.gz`).
- `--output`: (Optional) Default is `merged.vcf.gz` and saved at current
  working directory. Output file name without suffix.
- `--retained_snp_list`: (Optional) Default is None. Use a user-modified
  retained SNP list instead of the file IMMerge would create. The
  program will not create a new `*variants_retained.info.txt` when this
  option is provided. Must have columns: `SNP` (first), `ALT_Frq_combined`,
  `MAF_combined`, `Rsq_combined`, `Genotyped`.
- `--thread`: (Optional) Threads for multiprocessing.
    - Default 1. Integers only; values ≤ 0 are clamped to 1.
- `--missing`: (Optional, default 0) Number of missing files allowed per
  variant.
    - Cannot exceed total number of input files.
    - Missing genotypes are written as `.|.` (or `na_rep|na_rep`).
    - If `--missing 0`, only variants shared by all input files are kept.
- `--na_rep`: (Optional) Missing-value symbol. Default `.`. Ignored when
  `--missing` is 0.
- `--r2_threshold`: (Optional, default 0, i.e., no filtering) Only
  variants with combined R² ≥ threshold are retained.
- `--r2_output`: Default `z_transformation`. How combined imputation
  quality is computed. Valid values:
    - `z_transformation` **(recommended)**: Fisher z-transformation
    - `weighted_average`: weighted by number of individuals per file
    - `mean`, `min`, `max`: ignore missing values
    - `first`: take R² from the first file. Requires `--missing 0`.
- `--r2_offset`: (Optional) Default 0.001. Subtract from R² when R²=1 to
  avoid infinity under Fisher z.
- `--duplicate_id`: (Optional, default 0) Number of duplicated
  individuals in each input file (sanity check across sub-files).
  Duplicate IDs must be the first N columns and not mixed with unique
  IDs.
    - Example: if the first 100 individuals in each input are duplicated,
      set `--duplicate_id 100` so only the first set is kept in output.
    - From the second input file onward, the first 100 columns are
      skipped in the merged output.
- `--check_duplicate_id`: (Optional) Default False. Check for duplicate
  IDs, then rename non-first IDs to `ID:2`, `ID:3`, ...,
  `ID:index_of_input_file+1`.
- `--write_with`: (Optional) Default `bgzip`. Write output with
  `bgzip`. Supply a path like `/usr/bin/bgzip` to override.
- `--meta_info`: (Optional) Valid values: `{index of input file (1-based),
  'none', 'all'}`. Which `##` meta lines to include in the output.
  Default 1 (use meta information from the first input file).
- `--mixed_genotype_status`: (Optional) Default False. Case-insensitive
  `{0|1|True|False}`. Whether variants have more than one genotype status
  in input files. Use with `--genotyped_label` and `--imputed_label`.
  If False, output status is taken from the first input file (or the
  first file in which the SNP appears). If True, output status becomes
  `ALL` / `SOME` / `NONE`. Mixed inputs may produce a mix of labels.
- `--genotyped_label`: (Optional) Default `TYPED/TYPED_ONLY` (TOPMed).
  Label for genotyped variants; separate multiple values with `/`. Only
  evaluated when `--mixed_genotype_status` is True.
- `--imputed_label`: (Optional) Default `IMPUTED` (TOPMed). Label for
  imputed variants; separate multiple values with `/`. Only evaluated
  when `--mixed_genotype_status` is True.
- `--use_rsid`: (Optional) Default False. Set True when VCFs use rsID
  instead of `chr:pos:ref:alt`, to avoid duplicate IDs. New IDs in
  `chr:pos:ref:alt` format are created for merging. Use `make_info.py`
  with the same setting or follow the required info-file format.
- `--verbose`: (Optional) Default False. Emit additional progress
  information.
- `--help`: Print help and exit.

## make_info.py — CLI reference

Use this to generate `.info.gz` files from VCFs when they are not
already available.

- `--input`: (Required) Multiple input files are allowed. Must be
  gzipped or bgzipped VCF.
- `--output_dir`: (Optional) Directory for output files. Default is
  the current working directory.
- `--output_fn`: (Optional) Default is the input file name with suffix
  replaced by `.info.gz`.
- `--col_names`: (Optional) Default
  `['AF', 'MAF', 'R2', 'IMPUTED/TYPED/TYPED_ONLY']`. Column names of
  alt frequency, MAF, imputation quality, and genotype status,
  separated by spaces.
- `--thread`: (Optional) Default 1. Values ≤ 0 are clamped to 1.
- `--write_with`: (Optional) Default `bgzip`; `gzip` is also valid.
- `--use_rsid`: (Optional) Default False. Create `chr:pos:ref:alt`
  IDs from rsIDs to avoid duplicate IDs. Use the same setting when
  merging.
- `--mixed_genotype_status`: (Optional) Default False. Case-insensitive
  `{0|1|True|False}`. See notes under `merge_files.py`.
- `--genotyped_label`: (Optional) Default `TYPED/TYPED_ONLY`.
- `--imputed_label`: (Optional) Default `IMPUTED`.
- `--verbose`: (Optional) Default False.
- `--help`: Print help and exit.

---

## Examples

### Three-file merge

```bash
cd IMMerge
python src/IMMerge/merge_files.py \
    --input data_sample/sample_group1.dose.vcf.gz \
            data_sample/sample_group2.dose.vcf.gz \
            data_sample/sample_group3.dose.vcf.gz \
    --output output_sample/merged_sample \
    --check_duplicate_id true \
    --missing 1
```

### Generating info files first

```bash
cd IMMerge
python src/IMMerge/make_info.py \
    --input data_sample/sample_group1.dose.vcf.gz \
            data_sample/sample_group2.dose.vcf.gz \
            data_sample/sample_group3.dose.vcf.gz
```

### Using a user-supplied retained SNP list

```bash
cd IMMerge
python src/IMMerge/merge_files.py \
    --input data_sample/sample_group1.dose.vcf.gz \
            data_sample/sample_group2.dose.vcf.gz \
            data_sample/sample_group3.dose.vcf.gz \
    --output output_sample/modified_merged_sample \
    --retained_snp_list data_sample/modified_merged_sample_variants_retained.info.txt \
    --check_duplicate_id true \
    --missing 1
```

---

## Python module API

IMMerge can also be used as a Python module. Arguments are passed in a
dictionary and follow the same rules as the command line.

### Generate info files

```python
import IMMerge
args = {'--input': ['data_sample/sample_group1.dose.vcf.gz',
                    'data_sample/sample_group2.dose.vcf.gz',
                    'data_sample/sample_group3.dose.vcf.gz']}
IMMerge.write_info(args)
```

### Merge VCFs

```python
import IMMerge
args = {'--input': ['data_sample/sample_group1.dose.vcf.gz',
                    'data_sample/sample_group2.dose.vcf.gz',
                    'data_sample/sample_group3.dose.vcf.gz'],
        '--output': 'output_sample/merged_sample',
        '--check_duplicate_id': True,
        '--missing': 1}
IMMerge.run_merge_files(args)
```
