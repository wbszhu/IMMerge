# IMMerge: Merging imputation data at scale

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.1093%2Fbioinformatics%2Fbtac750-blue)](https://doi.org/10.1093/bioinformatics/btac750)

IMMerge combines multiple post-imputation VCF files into a single VCF,
correctly recomputing combined imputation quality (R²) with Fisher
z-transformation and weighted allele frequencies.

## Installation

Install the latest commit on `main` from this fork:

```bash
pip install git+https://github.com/wbszhu/IMMerge.git
```

Or clone and install (recommended if you plan to edit the code):

```bash
git clone https://github.com/wbszhu/IMMerge && cd IMMerge && pip install -e .
```

> **Note:** `pip install IMMerge` (from PyPI) installs the upstream
> [`belowlab/IMMerge`](https://github.com/belowlab/IMMerge), not this
> fork. Use the git URL above if you want the changes in this repo.

`bgzip` from [htslib](https://github.com/samtools/htslib) must be on your
`PATH` (used to write the merged `.vcf.gz`).

## Quick Start

```bash
python src/IMMerge/merge_files.py \
    --input file1.vcf.gz file2.vcf.gz file3.vcf.gz \
    --output merged_result \
    --missing 1
```

Each input VCF needs a matching `*.info.gz` in the same directory
(see [input file format](docs/usage.md#input-files)). Generate them
with `make_info.py` if you do not already have them.

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

See [`docs/`](docs/README.md) for the full user manual — CLI reference
for [merge_files.py](docs/usage.md#merge_filespy--cli-reference) and
[make_info.py](docs/usage.md#make_infopy--cli-reference),
[algorithm details](docs/algorithm.md),
and [Python module API](docs/usage.md#python-module-api).

## Citation

If you use IMMerge, please cite **both** the original paper and this fork.

**Paper** (original algorithm and implementation):

> Zhu W, Chen HH, Petty AS, Petty LE, Polikowsky HG, Gamazon ER, Below JE,
> Highland HM. *IMMerge: merging imputation data at scale*. Bioinformatics.
> 2023 Jan 1;39(1):btac750.
> doi: [10.1093/bioinformatics/btac750](https://doi.org/10.1093/bioinformatics/btac750).
> PMID: 36413071; PMCID: PMC9805583.

**Software** (this fork, for the specific implementation / bug fixes you used):

> Zhang L. *IMMerge (wbszhu fork)*, version 0.0.5. GitHub, 2026.
> https://github.com/wbszhu/IMMerge

## Fork contributors

<table>
<tr>
<td align="center">
  <a href="https://github.com/wbszhu">
    <img src="https://github.com/wbszhu.png" width="80" alt="Lu Zhang" /><br/>
    <sub><b>Lu Zhang</b></sub>
  </a><br/>
  <sub>maintainer</sub>
</td>
<td align="center">
  <a href="https://github.com/sethsh7">
    <img src="https://github.com/sethsh7.png" width="80" alt="Seth A. Sharp" /><br/>
    <sub><b>Seth A. Sharp</b></sub>
  </a><br/>
  <sub>SNP sorting fix (#1)</sub>
</td>
</tr>
</table>

For the authors of the original IMMerge (upstream) and the Bioinformatics
paper, see the [Citation](#citation) section above.

## License

MIT — see [LICENSE](LICENSE).
