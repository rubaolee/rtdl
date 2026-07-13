# Call For Review - Goal5161 Numba Nearest-Cell-MBR Seed

Please strictly review Goal5161.

## Files

- `src/rtdsl/partner_continuations.py`
- `tests/goal5158_vectorized_nearest_cell_mbr_seed_test.py`
- `tests/goal5161_numba_nearest_cell_mbr_seed_test.py`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_numba_seed_profile_pod.json`
- `Paper-reproduction-apps/x-hd-paper/data/manifest.json`
- `scripts/current_pod_ssh.py`
- `history/internal_docs/goal5161_numba_nearest_cell_mbr_seed_result_2026-07-08.md`

## Review Questions

1. Is the new `executor="auto|numpy|numba"` surface generic and app-neutral,
   rather than an X-HD-specific shortcut?
2. Does `executor="numpy"` preserve the Goal5158 vectorized path and public
   fallback behavior?
3. Does the Numba executor preserve the same deterministic tie-break semantics:
   lower MBR distance, then lower cell id, then lower target-point distance,
   then lower target id?
4. Do the tests prove Numba-vs-NumPy parity and fail closed on invalid executor
   values?
5. Does the source window avoid X-HD, paper, author, hd_exec, or Hausdorff
   identity leakage?
6. Does the POD artifact show author HDResult matching, `validation_mode=author-only`,
   and no authorized speedup/parity ratio?
7. Is the before/after comparison against Goal5160 fair as an RTDL-route
   comparison, while avoiding author parity/speedup claims?
8. Is the interpretation correct that seed is no longer the dominant measured
   route phase after Goal5161?
9. Is the `current_pod_ssh.py upload/download` addition a reasonable extension
   of the existing fixed-key POD wrapper discipline?
10. Does the manifest entry avoid overstating this as full paper reproduction,
    author algorithm equivalence, or denominator-aligned paper performance?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
```
