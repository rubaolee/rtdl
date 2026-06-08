# Handoff: Claude Review For Goal3834/Goal3835 Numba Partner Coverage

Please perform a read-only independent review of the current `main` work for
Goal3834 and Goal3835.

## Context

The user requirement is:

```text
For benchmark apps that need custom continuation logic, RTDL should provide a
Numba-based high-performance reference implementation when practical, so users
are not forced to write CuPy RawKernel/CUDA-C strings.
```

Recent work:

- Goal3834 added and measured a RayJoin public-CDB PIP same-contract Numba CUDA
  JIT scalar-count partner route.
- Goal3835 refreshed RT-DBSCAN prepared-grid and OptiX+prepared-grid evidence
  comparing CuPy vs Numba component continuations.

## Files To Inspect

- `scripts/goal3834_rayjoin_public_cdb_numba_pip_partner_baseline.py`
- `tests/goal3834_rayjoin_public_cdb_numba_pip_partner_baseline_test.py`
- `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_baseline_2026-06-07.md`
- `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/summary.json`
- `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/block_sweep/block_128.json`
- `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/block_sweep/block_256.json`
- `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/block_sweep/block_512.json`
- `docs/reports/goal3834_rayjoin_public_cdb_numba_pip_partner_a5000/block_sweep/block_1024.json`
- `docs/reports/goal3835_rt_dbscan_numba_partner_refresh_2026-06-08.md`
- `docs/reports/goal3835_rt_dbscan_numba_partner_refresh_a5000/summary.json`
- `docs/reports/goal3835_rt_dbscan_numba_partner_refresh_a5000_131k/summary.json`
- `tests/goal3835_rt_dbscan_numba_partner_refresh_test.py`
- `docs/learn/benchmark_partner_reference_matrix.md`
- Existing nearby baseline scripts:
  - `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py`
  - `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py`
  - `scripts/goal2403_rt_dbscan_repeat_probe.py`

## Review Questions

1. Does Goal3834 genuinely provide a no-RawKernel Numba same-contract RayJoin
   PIP scalar-count route, with no native app-specific engine logic?
2. Are the Goal3834 timing conclusions honest: count parity holds, Numba is
   valid but slower than CuPy for bounded scalar PIP, and RTDL/OptiX is not the
   recommended route for that exact row?
3. Does Goal3835 genuinely show RT-DBSCAN Numba prepared-grid and
   OptiX+Numba paths are competitive/high-performance versus comparable CuPy
   prepared-grid paths at 65,536 and 131,072 points?
4. Are claim boundaries intact: no release authorization, no public speedup
   claim, no paper-reproduction claim, no automatic partner selection, no true
   zero-copy claim?
5. Is the learner-facing matrix update accurate and not overclaiming?
6. What should be the next high-priority partner-coverage or performance debt?

## Expected Output

Write the review to:

`docs/reviews/goal3836_claude_review_goal3834_3835_numba_partner_coverage_2026-06-08.md`

Use one of the standard verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Lead with findings, then a short verdict summary. Do not edit source files
other than the requested review document.
