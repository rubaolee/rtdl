# Handoff: Gemini Review For Goal3749/Goal3750

Please perform an independent Gemini review of the Goal3749/Goal3750 work in
this repository.

## Context

The project requirement is that benchmark apps needing custom GPU continuation
logic should have high-performance Numba reference implementations, so users do
not need to write CuPy RawKernel or raw CUDA code. RTDL remains a generic
engine; app-owned logic stays outside native engine code.

Goal3749 adds a no-RawKernel Numba reference for RayJoin side-aware topology
continuation:

- `src/rtdsl/closed_shape_topology.py`
- `src/rtdsl/__init__.py`
- `tests/goal3749_rayjoin_side_aware_topology_numba_reference_test.py`
- `docs/reports/goal3749_rayjoin_side_aware_topology_numba_reference_2026-06-07.md`
- `docs/reports/goal3749_rayjoin_side_aware_topology_numba_a5000/summary.json`

Goal3750 updates the v2.9 benchmark adequacy ledger after Goal3749:

- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `tests/goal3740_benchmark_app_adequacy_after_goal3737_test.py`
- `tests/goal3747_numba_reference_adequacy_closure_test.py`
- `docs/reports/goal3740_benchmark_app_adequacy_after_goal3737_2026-06-07.md`
- `docs/reports/goal3750_numba_reference_adequacy_closure_after_goal3749_2026-06-07.md`

## Evidence Already Run By Codex

Local Windows:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3749_rayjoin_side_aware_topology_numba_reference_test tests.goal3740_benchmark_app_adequacy_after_goal3737_test tests.goal3747_numba_reference_adequacy_closure_test tests.goal3671_side_aware_owner_face_filter_test tests.goal3673_ordinal_selective_owner_side_filter_test
```

Result: 25 tests OK, 5 skipped.

A5000 pod:

```bash
PYTHONPATH=src:. python -m unittest tests.goal3749_rayjoin_side_aware_topology_numba_reference_test tests.goal3740_benchmark_app_adequacy_after_goal3737_test tests.goal3747_numba_reference_adequacy_closure_test tests.goal3671_side_aware_owner_face_filter_test tests.goal3673_ordinal_selective_owner_side_filter_test
```

Result: 25 tests OK.

A5000 same-contract timing artifact:

- 16,384 candidates: Numba/CuPy `9.899x`
- 65,536 candidates: Numba/CuPy `10.462x`
- 262,144 candidates: Numba/CuPy `16.521x`
- 1,048,576 candidates: Numba/CuPy `17.790x`
- all keep-count parity true
- all release/public-speedup/RT-core/whole-app claim flags false

## Review Questions

1. Does Goal3749 preserve generic engine boundaries, with RayJoin/topology
   policy at the Python/app-owned continuation layer rather than native
   app-specific engine logic?
2. Is the no-RawKernel Numba implementation correctly scoped as a partner
   reference and not a hidden automatic partner selection?
3. Does the sorted lookup/binary-search implementation preserve the existing
   public-id and prepared-ordinal semantics?
4. Is the A5000 timing artifact sufficient to mark the RayJoin Numba-reference
   pressure point closed, without authorizing broad public speedup or
   RayJoin-paper-reproduction claims?
5. Is Goal3750's update that `numba_reference_needed_apps` is empty justified?

## Required Output

Write your review to:

`docs/reviews/goal3751_gemini_review_goal3749_3750_rayjoin_numba_adequacy_2026-06-07.md`

Use one of the allowed verdict values:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Please include any required-before-next-step findings separately from optional
future work.
