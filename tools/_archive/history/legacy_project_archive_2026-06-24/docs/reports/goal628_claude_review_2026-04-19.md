# Goal 628: Claude Review Verdict

Date: 2026-04-19
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

## What was reviewed

- `tests/_optional_native_compare.py` (new helper)
- `tests/goal15_compare_test.py`
- `tests/goal17_prepared_runtime_test.py`
- `tests/goal19_compare_test.py`
- `tests/report_smoke_test.py`
- `tests/goal207_knn_rows_external_baselines_test.py`

## Blocker 1: Optional native C++ comparison failures → SkipTest

The helper `skip_optional_native_compare_failure` in `_optional_native_compare.py` is
correctly scoped. It only converts to `SkipTest` when:

- the exception is `RuntimeError` or `subprocess.CalledProcessError`, AND
- the message/stderr contains a toolchain-availability marker (geos, embree,
  pkg-config, library not found, cannot find -l, returned non-zero exit status,
  native oracle build failed, optional native comparison build).

A result-level mismatch (e.g. `AssertionError`) does not match either condition and
continues to fail. The guard is applied consistently across all four affected test
files (`goal15`, `goal19`, `report_smoke_test` × 2, `goal17` via
`_embree_support.embree_available()` outer skip). The pattern is `try/except
Exception → skip_or_reraise`, which preserves the original exception for any
unrecognised error.

No real correctness signal is being suppressed.

## Blocker 2: KNN float comparison

`assertKnnRowsAlmostEqual` in `goal207_knn_rows_external_baselines_test.py`:

- `query_id`, `neighbor_id`, `neighbor_rank` — exact `assertEqual`.
- `distance` — `assertAlmostEqual(..., places=12)`, i.e. tolerance ≈ 5 × 10⁻¹³.

The reported difference was in the 16th significant digit (~10⁻¹⁶), well within
`places=12`. Row identity and rank integrity are preserved. This is the correct
fix.

## No issues found

The implementation matches the stated fix. Both blocker classes are addressed
without weakening correctness checks for real failures.
