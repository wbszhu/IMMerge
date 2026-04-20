"""
Regression tests for IMMerge.

Layered so the cheap tests run unconditionally and the expensive ones skip
gracefully when their environment is missing:

1. Package-level smoke tests (import, version, public API).           Always run.
2. CLI smoke tests (--help exit code).                                Always run.
3. Pandas `bfill` regression guard for `get_genotype_status`.         Always run.
4. get_snp_list regression on the sample data.                        Needs data_sample/.
5. Full merge_files.py end-to-end + output diff.                      Needs bgzip.
"""
from __future__ import annotations

import gzip
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tests.conftest import (
    OUTPUT_SAMPLE,
    REPO_ROOT,
    SRC_DIR,
    requires_bgzip,
    requires_sample_data,
)

MERGE_SCRIPT = SRC_DIR / "merge_files.py"
MAKE_INFO_SCRIPT = SRC_DIR / "make_info.py"
FIXTURES_EXPECTED = Path(__file__).parent / "fixtures" / "expected"


# -------------------------------------------------------------------------
# 1. Package smoke
# -------------------------------------------------------------------------

class TestPackage:
    def test_version_is_semver_string(self):
        import IMMerge

        assert isinstance(IMMerge.__version__, str)
        # X.Y.Z minimum (three dot-separated components)
        assert IMMerge.__version__.count(".") >= 2

    def test_public_api_is_callable(self):
        import IMMerge

        assert callable(IMMerge.run_merge_files)
        assert callable(IMMerge.write_info)

    def test_version_matches_pyproject(self):
        """Guard against the two copies of the version string drifting apart."""
        import IMMerge

        pyproject = (REPO_ROOT / "pyproject.toml").read_text()
        # Crude but dependency-free: look for `version = "X.Y.Z"`
        for line in pyproject.splitlines():
            stripped = line.strip()
            if stripped.startswith("version") and "=" in stripped:
                declared = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                assert declared == IMMerge.__version__, (
                    f"pyproject.toml declares {declared!r} but IMMerge.__version__ is "
                    f"{IMMerge.__version__!r}"
                )
                return
        pytest.fail("Could not find a `version = \"...\"` line in pyproject.toml")


# -------------------------------------------------------------------------
# 2. CLI smoke
# -------------------------------------------------------------------------

class TestCliHelp:
    """`--help` exiting 0 is the simplest proof that argparse, the package
    imports, and the dependency pins are all consistent. If any of these
    break, other tests will too — but this is the first to fail and tells
    you exactly where to look."""

    def test_merge_files_help(self):
        result = subprocess.run(
            [sys.executable, str(MERGE_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert "--input" in result.stdout
        assert "--r2_output" in result.stdout

    def test_make_info_help(self):
        result = subprocess.run(
            [sys.executable, str(MAKE_INFO_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert "--input" in result.stdout


# -------------------------------------------------------------------------
# 3. Pandas bfill regression
# -------------------------------------------------------------------------

class TestBfillRegression:
    """Regression guard for the pandas 2.x compatibility fix at
    `src/IMMerge/get_SNP_list.py:109` — `fillna(method='backfill', axis=1)`
    was replaced with `.bfill(axis=1)`. If a future pandas release ever
    changes `bfill` semantics, this test fails loudly before the change
    can silently corrupt merged results."""

    def test_bfill_matches_deprecated_backfill(self):
        df = pd.DataFrame(
            {
                "Genotyped_group1": [np.nan, "TYPED", np.nan],
                "Genotyped_group2": ["IMPUTED", np.nan, np.nan],
                "Genotyped_group3": [np.nan, "IMPUTED", "TYPED"],
            }
        )
        result = df.bfill(axis=1)["Genotyped_group1"].tolist()
        assert result == ["IMPUTED", "TYPED", "TYPED"]

    def test_get_genotype_status_uses_bfill(self):
        """If someone re-introduces `fillna(method=...)` this will catch it
        on pandas >= 2.0."""
        from IMMerge.get_SNP_list import get_genotype_status

        df = pd.DataFrame(
            {
                "Genotyped_group1": [np.nan, "TYPED", np.nan],
                "Genotyped_group2": ["IMPUTED", np.nan, np.nan],
                "Genotyped_group3": [np.nan, "IMPUTED", "TYPED"],
            }
        )
        get_genotype_status(
            df,
            mixed_genotype=False,
            genotyped_labels="TYPED/TYPED_ONLY",
            imputed_labels="IMPUTED",
            number_of_input_files=3,
        )
        assert "Genotyped" in df.columns
        assert df["Genotyped"].tolist() == ["IMPUTED", "TYPED", "TYPED"]


# -------------------------------------------------------------------------
# 4. get_snp_list regression (no bgzip needed)
# -------------------------------------------------------------------------

@requires_sample_data
class TestGetSnpListRegression:
    """Exercises the SNP-filtering and combined-stat code path against the
    committed golden in `tests/fixtures/expected/`. Does NOT need bgzip —
    only reads `.info.gz` files and writes plain-text info tables.

    The golden is generated from the current code (see `tests/README.md`
    for regeneration instructions). It is the authoritative reference for
    info-table format and content; `output_sample/` in the repo root may
    be stale from an earlier version (v0.0.3 had a different column order
    and used `cap_adj` instead of `offset_adj`).
    """

    def _run_get_snp_list(self, tmp_path: Path, sample_inputs: list[str]) -> Path:
        from IMMerge.get_SNP_list import get_snp_list
        from IMMerge.process_args import process_args

        output_prefix = tmp_path / "merged_sample"
        flags = process_args(
            [
                "--input", *sample_inputs,
                "--output", str(output_prefix),
                "--missing", "1",
                "--check_duplicate_id", "True",
            ]
        )
        get_snp_list(flags)
        return output_prefix

    def test_variants_retained_matches_golden(self, tmp_path, sample_inputs):
        output_prefix = self._run_get_snp_list(tmp_path, sample_inputs)
        produced = output_prefix.parent / f"{output_prefix.name}_variants_retained.info.txt"
        expected = FIXTURES_EXPECTED / "merged_sample_variants_retained.info.txt"
        assert produced.exists(), f"expected output missing: {produced}"
        assert produced.read_text() == expected.read_text(), (
            "Retained-variant info table diverges from tests/fixtures/expected/. "
            "If this is an intentional behavior change, regenerate the golden "
            "(see tests/README.md) and commit the updated fixture."
        )

    def test_variants_excluded_matches_golden(self, tmp_path, sample_inputs):
        output_prefix = self._run_get_snp_list(tmp_path, sample_inputs)
        produced = output_prefix.parent / f"{output_prefix.name}_variants_excluded.info.txt"
        expected = FIXTURES_EXPECTED / "merged_sample_variants_excluded.info.txt"
        assert produced.exists()
        assert produced.read_text() == expected.read_text(), (
            "Excluded-variant info table diverges from tests/fixtures/expected/. "
            "See tests/README.md for how to regenerate the golden."
        )


# -------------------------------------------------------------------------
# 5. Full end-to-end merge
# -------------------------------------------------------------------------

@requires_sample_data
@requires_bgzip
class TestFullMergeEndToEnd:
    """Full pipeline: runs `merge_files.py` on data_sample/ and diffs every
    artifact against output_sample/. This is the most valuable regression
    test — if it passes, no refactor has silently changed user-visible
    behavior. Skipped when bgzip or sample data are unavailable."""

    @pytest.fixture
    def merged_output_prefix(self, tmp_path, sample_inputs):
        """Run the merge once per test class, return the tmp output prefix."""
        output_prefix = tmp_path / "merged_sample"
        cmd = [
            sys.executable, str(MERGE_SCRIPT),
            "--input", *sample_inputs,
            "--output", str(output_prefix),
            "--check_duplicate_id", "True",
            "--missing", "1",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=REPO_ROOT
        )
        assert result.returncode == 0, (
            f"merge_files.py failed:\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
        return output_prefix

    def test_info_tables_match_golden(self, merged_output_prefix):
        for suffix in ("_variants_retained.info.txt", "_variants_excluded.info.txt"):
            produced = Path(str(merged_output_prefix) + suffix)
            expected = FIXTURES_EXPECTED / f"merged_sample{suffix}"
            assert produced.exists()
            assert produced.read_text() == expected.read_text(), (
                f"{suffix} diverges from tests/fixtures/expected/"
            )

    def test_merged_vcf_data_lines_match_reference(self, merged_output_prefix):
        """Compare decompressed VCF data rows (skip header lines with
        timestamps and absolute paths). Uses `output_sample/merged_sample.vcf.gz`
        as the reference — if this fails and the only difference is column
        reorder or metadata, the reference is stale (from v0.0.3) and should
        be regenerated on a machine with bgzip."""
        produced_path = Path(str(merged_output_prefix) + ".vcf.gz")
        expected_path = OUTPUT_SAMPLE / "merged_sample.vcf.gz"
        assert produced_path.exists()
        if not expected_path.exists():
            pytest.skip(f"reference VCF missing: {expected_path}")

        def _data_lines(path: Path) -> list[str]:
            with gzip.open(path, "rt") as fh:
                return [ln for ln in fh if not ln.startswith("##")]

        produced = _data_lines(produced_path)
        expected = _data_lines(expected_path)
        assert produced == expected, (
            "Merged VCF data rows (non-## lines) diverge from output_sample/. "
            "If this is the first run after the seth-edits sort fix, regenerate "
            "the reference: run the same merge command used to produce "
            "output_sample/merged_sample.vcf.gz with the current code."
        )

    def test_log_file_is_created(self, merged_output_prefix):
        log_path = Path(str(merged_output_prefix) + ".log")
        assert log_path.exists()
        content = log_path.read_text()
        assert "IMMerge Version" in content
        assert "Duration" in content
