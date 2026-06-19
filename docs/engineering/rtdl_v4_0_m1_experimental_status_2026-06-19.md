# RTDL V4.0 M1 Experimental Status

Status: experimental engineering evidence, not current release.
Date: 2026-06-19.
Latest validated implementation head: `5f239ab1079edf264a915be99e0f7295fc1ea887`.
Latest validated route-code tree: `c0f7054e7ab09068bee4ea02b2202741dcabf96b`.

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

- host program is Python with evidence-backed CuPy or Numba CUDA device arrays;
- inputs are caller-owned CUDA `ids`, `x`, and `y` point columns;
- outputs are caller-owned CUDA `query_ids`, `neighbor_counts`, and
  `threshold_flags` columns;
- output shape is fixed one row per query, not variable-length neighbor rows;
- nonzero caller CUDA streams propagate through prepare and query;
- different nonzero prepare/query streams fail closed until an explicit
  event/wait contract exists;
- native route synchronizes before return;
- async completion is not claimed.
- evidence-backed input protocols are the CuPy adapter and
  `__cuda_array_interface__`;
- a CuPy-backed DLPack-only wrapper smoke exists for the generic DLPack adapter;
  arbitrary DLPack capsule ownership/deleter semantics and PyTorch remain
  target surfaces without full route evidence.

## Evidence

| Evidence | Path | Reading |
| --- | --- | --- |
| Stream and pointer smoke | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json` | Passing snapshot for pointer identity, pointer echo, caller-stream propagation, and blocked promotion flags. |
| Parity matrix | `docs/reports/v4_0_m1_fixed_radius_cupy_parity_matrix_2026-06-19.json` | Passing positive cases plus fail-closed zero-length CuPy pointer behavior. |
| No-host-stage probe | `docs/reports/v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json` | Authorizes named-column no-host-stage wording; does not authorize true-zero-copy wording. |
| Benchmark probe | `docs/reports/v4_0_m1_fixed_radius_cupy_benchmark_probe_2026-06-19.json` | Raw route timing smoke only; does not authorize public speedup or RT-core speedup wording. |
| Same-stream ordering probe | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_ordering_probe_2026-06-19.json` | Authorizes same-stream producer -> RTDL -> consumer ordering; does not authorize cross-stream event waits or async wording. |
| Numba CUDA Array Interface smoke | `docs/reports/v4_0_m1_fixed_radius_numba_cuda_array_interface_smoke_2026-06-19.json` | Authorizes Numba `DeviceNDArray` columns through `__cuda_array_interface__`; does not authorize a full Numba partner surface, PyTorch, or DLPack. |
| DLPack bridge wrapper smoke | `docs/reports/v4_0_m1_fixed_radius_dlpack_bridge_smoke_2026-06-19.json` | Authorizes a CuPy-backed DLPack-only wrapper through the generic DLPack adapter; does not authorize arbitrary DLPack capsule semantics or PyTorch. |
| True-zero-copy wording consensus | `docs/reviews/codex_v4_m1_true_zero_copy_wording_consensus_2026-06-19.md` | Keeps public true-zero-copy wording blocked. |
| Release-positioning consensus | `docs/reviews/codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md` | Keeps v3.0.2 as current release and V4 as experimental M1 evidence. |
| Release-candidate blocker manifest | `docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json` | Keeps `v4_release_candidate` absent until the M8 release-candidate packet and blockers close. |
| Front-door claim scan | `docs/reports/v4_0_current_front_door_claim_boundary_scan_2026-06-19.json` | Confirms current front-door docs resolve to v3.0.2 and do not positively publish blocked V4 claims. |

Current reproducibility gate:

```bash
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_active
```

Latest Linux validation on `192.168.1.20` for implementation head
`5f239ab1079edf264a915be99e0f7295fc1ea887`:

- `v4_active`: 46 tests, pass;
- `make build-optix`: pass;
- same-stream ordering probe: pass;
- Numba CUDA Array Interface smoke: pass;
- DLPack bridge wrapper smoke: pass;
- `git diff --check`: pass.

Current source-tree `v4_active` gate after the release-candidate blocker
manifest and front-door claim-scan guards: 48 tests, pass locally.

## Release-Candidate Boundary

The source tree intentionally does not expose a passing `v4_release_candidate`
test-matrix group yet. That name is reserved for the future M8 release-candidate
packet, after the explicit blocker list closes.

Current machine-readable blocker manifest:

`docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json`

## Allowed Public-Safe Wording

- "V4.0 M1 has an experimental CuPy fixed-radius count/threshold GPU operator route."
- "The route borrows caller-owned CUDA input columns and writes caller-owned CUDA output columns."
- "Zero-copy device-column handoff with no observed host staging of named columns."
- "Nonzero caller CUDA streams are propagated through prepare and query; the route synchronizes before return."
- "Same-stream producer -> RTDL prepare/query -> consumer ordering is validated on one nondefault CuPy CUDA stream."
- "Different nonzero prepare/query CUDA streams are rejected until an explicit event/wait contract exists."
- "A CuPy-backed DLPack-only wrapper smoke exercises the generic DLPack adapter."
- "Raw route-scoped timing probe exists; it does not authorize public speedup wording."

## Blocked Wording

- V4.0 is the current release.
- Stable V4 SDK.
- Package install, PyPI, or wheel support.
- Generated bindings or public multi-language C ABI release.
- True zero-copy, end-to-end zero-copy, no copies, no staging, or no H2D copies.
- Async, nonblocking, or returns before GPU work completes.
- Cross-stream event wait support.
- RT-core speedup, RTX speedup, RTDL is faster, or broad performance claims.
- Full Numba partner surface, PyTorch, arbitrary DLPack capsules, or full
  DLPack route support.

## Current Claim Flags

| Claim | Status |
| --- | --- |
| Current release/front-door promotion | blocked |
| Stable SDK/package install | blocked |
| Public true-zero-copy | blocked |
| Async/nonblocking completion | blocked |
| Same-stream ordering | experimental M1 evidence |
| Cross-stream event waits | blocked |
| Public speedup | blocked |
| RTX/RT-core speedup | blocked |
| CuPy route evidence | experimental M1 evidence |
| Numba `DeviceNDArray` via CUDA Array Interface | experimental M1 evidence |
| DLPack bridge wrapper over CuPy-owned arrays | experimental M1 evidence |
| Full Numba partner surface | blocked |
| PyTorch route evidence | not yet present |
| Full DLPack capsule/framework route evidence | blocked |

PyTorch preflight on `192.168.1.20`, 2026-06-19: blocked by runtime
availability. The host has CuPy/Numba but no `torch` module; there is no
passwordless sudo, `python3.12-venv` is unavailable, and the attempted user-site
Torch dry-run was unbounded and stopped. No PyTorch route support wording is
authorized until an actual CUDA tensor smoke passes.

## Next Gates

1. Keep the M1 route reproducible on current head.
2. Add cross-stream event/wait ownership only after an explicit owner/event contract exists.
3. Add PyTorch, DLPack, or broader Numba partner evidence before saying those surfaces are validated.
4. Use RTX-class hardware before any RT-core speed discussion.
5. Keep the release-candidate blocker manifest current while `v4_release_candidate` remains absent from the passing test matrix.
6. Only after an M8 release-candidate packet exists and the blocker manifest is closed, expose a `v4_release_candidate` gate and reconsider whether V4 can become the current front door.
