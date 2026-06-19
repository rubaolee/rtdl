# RTDL V4.0 M1 Experimental Status

Status: experimental engineering evidence, not current release.
Date: 2026-06-19.
Latest validated head: `95b724159e9e6e0e1ab734850ceede2c3a7ca692`.
Latest validated tree: `f4b7ab6ba3edede33c106ba451f9d322f590d462`.

This packet summarizes the current V4.0 M1 state after the fixed-radius CuPy
device-array route landed. It is an engineering status packet, not a release
packet, stable SDK promise, package-install promise, public speedup claim, or
public true-zero-copy claim.

## Release Position

V4.0 is not the current user release/front door.

The current source-tree release remains `v3.0.2`. The V4.0 M1 work is an
active engineering preview for the Python GPU RT-core operator direction.

This status follows the 2-AI release-positioning consensus:

`docs/reviews/codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md`

## M1 Product Route

Route: `fixed_radius_count_threshold_2d`

Python API:

- `rtdsl.prepare_v4_fixed_radius_count_threshold_2d`
- `rtdsl.run_v4_fixed_radius_count_threshold_2d`

Implemented contract:

- host program is Python with CuPy CUDA arrays;
- inputs are caller-owned CUDA `ids`, `x`, and `y` point columns;
- outputs are caller-owned CUDA `query_ids`, `neighbor_counts`, and
  `threshold_flags` columns;
- output shape is fixed one row per query, not variable-length neighbor rows;
- nonzero caller CUDA streams propagate through prepare and query;
- native route synchronizes before return;
- async completion is not claimed.

## Evidence

| Evidence | Path | Reading |
| --- | --- | --- |
| Stream and pointer smoke | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json` | Passing snapshot for pointer identity, pointer echo, caller-stream propagation, and blocked promotion flags. |
| Parity matrix | `docs/reports/v4_0_m1_fixed_radius_cupy_parity_matrix_2026-06-19.json` | Passing positive cases plus fail-closed zero-length CuPy pointer behavior. |
| No-host-stage probe | `docs/reports/v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json` | Authorizes named-column no-host-stage wording; does not authorize true-zero-copy wording. |
| Benchmark probe | `docs/reports/v4_0_m1_fixed_radius_cupy_benchmark_probe_2026-06-19.json` | Raw route timing smoke only; does not authorize public speedup or RT-core speedup wording. |
| True-zero-copy wording consensus | `docs/reviews/codex_v4_m1_true_zero_copy_wording_consensus_2026-06-19.md` | Keeps public true-zero-copy wording blocked. |
| Release-positioning consensus | `docs/reviews/codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md` | Keeps v3.0.2 as current release and V4 as experimental M1 evidence. |

Current reproducibility gate:

```bash
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_active
```

Latest Linux validation on `192.168.1.20` for
`95b724159e9e6e0e1ab734850ceede2c3a7ca692`:

- `v4_active`: 32 tests, pass;
- `git diff --check`: pass.

## Allowed Public-Safe Wording

- "V4.0 M1 has an experimental CuPy fixed-radius count/threshold GPU operator route."
- "The route borrows caller-owned CUDA input columns and writes caller-owned CUDA output columns."
- "Zero-copy device-column handoff with no observed host staging of named columns."
- "Nonzero caller CUDA streams are propagated through prepare and query; the route synchronizes before return."
- "Raw route-scoped timing probe exists; it does not authorize public speedup wording."

## Blocked Wording

- V4.0 is the current release.
- Stable V4 SDK.
- Package install, PyPI, or wheel support.
- Generated bindings or public multi-language C ABI release.
- True zero-copy, end-to-end zero-copy, no copies, no staging, or no H2D copies.
- Async, nonblocking, or returns before GPU work completes.
- RT-core speedup, RTX speedup, RTDL is faster, or broad performance claims.
- CuPy/Numba/PyTorch validated unless separate route evidence exists for each named framework.

## Current Claim Flags

| Claim | Status |
| --- | --- |
| Current release/front-door promotion | blocked |
| Stable SDK/package install | blocked |
| Public true-zero-copy | blocked |
| Async/nonblocking completion | blocked |
| Public speedup | blocked |
| RTX/RT-core speedup | blocked |
| CuPy route evidence | experimental M1 evidence |
| Numba route evidence | not yet present |
| PyTorch route evidence | not yet present |
| DLPack route evidence | not yet present |

## Next Gates

1. Keep the M1 route reproducible on current head.
2. Add producer-stream to prepare to query to consumer-stream ordering proof before widening stream wording.
3. Add Numba, PyTorch, or DLPack evidence before saying those frameworks are validated.
4. Use RTX-class hardware before any RT-core speed discussion.
5. Define a future `v4_release_candidate` gate distinct from `v4_active`.
6. Only after an M8 release-candidate packet exists, reconsider whether V4 can become the current front door.
