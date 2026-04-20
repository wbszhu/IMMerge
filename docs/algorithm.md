# IMMerge Algorithm Details

How IMMerge combines imputation quality (R²), minor allele frequency
(MAF), and alternate allele frequency (AF) across multiple input files.

For command-line usage, see the [usage guide](usage.md).
For the original description, see the
[Bioinformatics 2023 paper](https://doi.org/10.1093/bioinformatics/btac750).

## Merging strategy

Variants are merged across input files with an outer join on
`(SNP, POS, REF(0), ALT(1))`, so that:

- a variant present in any input file is considered for the output;
- a variant with flipped `REF`/`ALT` in a different file is correctly
  treated as a distinct record rather than silently combined.

A variant is **retained** when:

- it appears in at least `N − --missing` of the `N` input files, and
- its combined R² is ≥ `--r2_threshold`.

All other variants go into `*_variants_excluded.info.txt`.

## Combined imputation quality (R²)

Controlled by `--r2_output`. Default: `z_transformation`.

### Fisher z-transformation (recommended)

Reference: [Silver & Dunlap, 1987](https://doi.org/10.1037/0021-9010.72.1.146).

1. Adjust each input's R² so that R² = 1 is not singular:
   $r^2 = r^2 - r^2_{\text{offset}}$ (default offset 0.001).
2. z-transform: $z = \tfrac{1}{2} \ln\!\bigl(\tfrac{1 + r}{1 - r}\bigr)$.
3. Take a weighted average of $z$ across input files, weighting by the
   number of individuals $N_i$ in each file.
4. Convert back to r with the inverse transformation:
   $r = \tfrac{e^{z} - e^{-z}}{e^{z} + e^{-z}}$.
5. Combined quality is $r^2$.

### Weighted average

$$R^2_{\text{combined}} = \frac{\sum_{i=1}^{n} R_i^2 \cdot N_i}{\sum_{i=1}^{n} N_i}$$

where $R^2_i$ is the R² of the $i$-th input file and $N_i$ is the number
of individuals in it. Missing values are ignored.

**Worked example**. A variant with:

- File #1: R² = 0.3, N = 1000
- File #2: missing (skipped), N = 2000
- File #3: R² = 0.2, N = 3000

gives weighted R² = (0.3 × 1000 + 0.2 × 3000) / (1000 + 3000) = **0.225**.

### Other methods

- `mean` — unweighted mean of non-missing R².
- `min`, `max` — min / max of non-missing R².
- `first` — take R² from the first input file (requires `--missing 0`,
  otherwise a variant may be missing from file 1 and the output R² is
  undefined).

## Combined MAF

$$\text{MAF}_{\text{combined}} = \frac{\sum_{i=1}^{n} \text{MAF}_i \cdot N_i}{\sum_{i=1}^{n} N_i}$$

MAF uses the same weighted-average formula as `weighted_average` R²,
ignoring missing values.

## Combined AF

AF uses the same weighted-average formula as MAF.

## Missing-value handling

- Missing values do not contribute to any weighted sum or denominator.
- Under Fisher z, variants with R² = 1 are first decreased by
  `--r2_offset` (default 0.001) to avoid $\ln(0)$.
- Sort order of variants in output info tables follows the input VCF
  order (by `POS` and per-input-file row index), so that the info
  tables and the merged VCF stay aligned even at multiallelic sites.
