# IMMerge: Merging imputation data at scale

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.1093%2Fbioinformatics%2Fbtac750-blue)](https://doi.org/10.1093/bioinformatics/btac750)

IMMerge combines multiple post-imputation VCF files into a single VCF,
correctly recomputing combined imputation quality (R²) with Fisher
z-transformation and weighted allele frequencies.

## Installation

```bash
pip install IMMerge
```

Or from source:

```bash
git clone https://github.com/wbszhu/IMMerge && cd IMMerge && pip install .
```

`bgzip` from [htslib](https://github.com/samtools/htslib) must be on your
`PATH` (used to write the merged `.vcf.gz`).

## Quick Start

```bash
python src/IMMerge/merge_files.py \
    --input file1.vcf.gz file2.vcf.gz file3.vcf.gz \
    --output merged_result \
    --missing 1
```

Each input VCF needs a matching `*.info.gz` in the same directory.
Generate them with `make_info.py` if you do not already have them.

## Output Files

With `--output <prefix>`, IMMerge writes:

| File | Description |
| --- | --- |
| `<prefix>.vcf.gz` | Merged, bgzipped VCF with combined `AF` / `MAF` / `R2` in the `INFO` column. |
| `<prefix>_variants_retained.info.txt` | Info table for variants that passed `--r2_threshold` and `--missing` filters. |
| `<prefix>_variants_excluded.info.txt` | Info table for variants that were filtered out. |
| `<prefix>.log` | Run summary: sample counts, retained/excluded variant counts, execution time. |
| `<prefix>_dup_IDs.txt` | Present only with `--check_duplicate_id true`; lists renamed duplicate sample IDs. |

## Documentation

See [`docs/`](docs/README.md) for the full user manual — CLI reference,
input file format, algorithm details, and the Python module API.

## Citation

Zhu W, Chen HH, Petty AS, Petty LE, Polikowsky HG, Gamazon ER, Below JE,
Highland HM. *IMMerge: merging imputation data at scale*. Bioinformatics.
2023 Jan 1;39(1):btac750. doi: [10.1093/bioinformatics/btac750](https://doi.org/10.1093/bioinformatics/btac750).
PMID: 36413071; PMCID: PMC9805583.

## License

MIT — see [LICENSE](LICENSE).
