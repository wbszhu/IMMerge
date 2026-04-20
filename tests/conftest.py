"""
Shared fixtures and markers for the IMMerge test suite.

Two environmental things can disable portions of the suite; both are detected
here and exposed as pytest skip-markers:

- `bgzip` (from htslib) — required by `merge_files.py` to write the merged
  VCF. Tests that invoke the full merge pipeline skip when it is not on PATH.
- `data_sample/` and `output_sample/` — the reference input and expected
  output directories. They are `.gitignore`d in this repo (the original
  author kept them out of version control), so tests that depend on them
  skip when they are not present on disk.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_SAMPLE = REPO_ROOT / "data_sample"
OUTPUT_SAMPLE = REPO_ROOT / "output_sample"
SRC_DIR = REPO_ROOT / "src" / "IMMerge"


def _bgzip_available() -> bool:
    return shutil.which("bgzip") is not None


def _sample_data_available() -> bool:
    required = [
        DATA_SAMPLE / "sample_group1.dose.vcf.gz",
        DATA_SAMPLE / "sample_group1.info.gz",
        DATA_SAMPLE / "sample_group2.dose.vcf.gz",
        DATA_SAMPLE / "sample_group2.info.gz",
        DATA_SAMPLE / "sample_group3.dose.vcf.gz",
        DATA_SAMPLE / "sample_group3.info.gz",
        OUTPUT_SAMPLE / "merged_sample_variants_retained.info.txt",
        OUTPUT_SAMPLE / "merged_sample_variants_excluded.info.txt",
    ]
    return all(p.exists() for p in required)


requires_bgzip = pytest.mark.skipif(
    not _bgzip_available(),
    reason="bgzip (htslib) not on PATH — install via `brew install htslib` "
    "or `apt install tabix` to run the full merge pipeline",
)

requires_sample_data = pytest.mark.skipif(
    not _sample_data_available(),
    reason="data_sample/ or output_sample/ missing (both are .gitignored; "
    "these tests require the original author's sample fixtures to be present locally)",
)


@pytest.fixture
def sample_inputs() -> list[str]:
    """Paths to the three sample VCFs used in the README Quick Start example."""
    return [
        str(DATA_SAMPLE / "sample_group1.dose.vcf.gz"),
        str(DATA_SAMPLE / "sample_group2.dose.vcf.gz"),
        str(DATA_SAMPLE / "sample_group3.dose.vcf.gz"),
    ]
