# RTDL V4.0 M1 Experimental Status

Status: experimental engineering evidence, not current release.
Date: 2026-06-19.
Latest validated source-tree head: `22bf64678858b8ad7606f32428d918f511f5f179`.
Latest validated source-tree tree: `f0051bb11ac742789a8bfd12d19201123daeecdb`.

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
- different nonzero prepare/query streams are ordered by a native
  prepare-ready event owned by the prepared fixed-radius handle;
- native route synchronizes before return;
- async completion is not claimed.
- evidence-backed input protocols are the CuPy adapter and
  `__cuda_array_interface__`;
- a CuPy-backed DLPack-only wrapper smoke exists for the generic DLPack adapter;
- a fixed-radius M1 legacy DLPack capsule route has stream, pointer, output,
  consume-once, and deleter-once evidence;
- arbitrary framework-neutral DLPack and PyTorch remain target surfaces without
  full route evidence.

## Evidence

| Evidence | Path | Reading |
| --- | --- | --- |
| Stream and pointer smoke | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json` | Passing snapshot for pointer identity, pointer echo, caller-stream propagation, and blocked promotion flags. |
| Parity matrix | `docs/reports/v4_0_m1_fixed_radius_cupy_parity_matrix_2026-06-19.json` | Passing positive cases plus fail-closed zero-length CuPy pointer behavior. |
| No-host-stage probe | `docs/reports/v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json` | Authorizes named-column no-host-stage wording; does not authorize true-zero-copy wording. |
| Benchmark probe | `docs/reports/v4_0_m1_fixed_radius_cupy_benchmark_probe_2026-06-19.json` | Raw route timing smoke only; does not authorize public speedup or RT-core speedup wording. |
| Stream ordering probe | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_ordering_probe_2026-06-19.json` | Authorizes same-stream producer -> RTDL -> consumer ordering and fixed-radius M1 distinct prepare/query stream ordering via native prepare-ready event; does not authorize async, public event ownership, full external-stream ownership, or general cross-stream behavior. |
| Numba CUDA Array Interface smoke | `docs/reports/v4_0_m1_fixed_radius_numba_cuda_array_interface_smoke_2026-06-19.json` | Authorizes Numba `DeviceNDArray` columns through `__cuda_array_interface__`; superseded by the fuller M1 partner-surface probe below. |
| Numba M1 `DeviceNDArray` fixed-radius route probe | `docs/reports/v4_0_m1_fixed_radius_numba_partner_surface_probe_2026-06-19.json` | Authorizes bounded M1 Numba `DeviceNDArray` wording for parity, same-stream propagation, pointer echo, caller-owned output columns, and prepared-handle reuse while search columns remain alive; does not authorize arbitrary Numba program acceleration. |
| Numba route-boundary consensus | `docs/reviews/codex_v4_m1_numba_surface_2ai_consensus_2026-06-19.md` | Keeps `full_numba_partner_surface` open while accepting bounded M1 `DeviceNDArray` fixed-radius route evidence. |
| DLPack bridge wrapper smoke | `docs/reports/v4_0_m1_fixed_radius_dlpack_bridge_smoke_2026-06-19.json` | Authorizes a CuPy-backed DLPack-only wrapper through the generic DLPack adapter; does not authorize arbitrary DLPack capsule semantics or PyTorch. |
| DLPack capsule probe | `docs/reports/v4_0_m1_fixed_radius_dlpack_capsule_probe_2026-06-19.json` | Authorizes narrow fixed-radius M1 legacy DLPack capsule wording for stream argument propagation, pointer identity, native pointer echo, output correctness, and consume-once/deleter-once guards; does not authorize arbitrary framework-neutral DLPack or PyTorch. |
| True-zero-copy wording consensus | `docs/reviews/codex_v4_m1_true_zero_copy_wording_consensus_2026-06-19.md` | Keeps public true-zero-copy wording blocked. |
| Release-positioning consensus | `docs/reviews/codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md` | Keeps v3.0.2 as current release and V4 as experimental M1 evidence. |
| Release-candidate blocker manifest | `docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json` | Keeps `v4_release_candidate` absent until the M8 release-candidate packet and blockers close. |
| Front-door claim scan | `docs/reports/v4_0_current_front_door_claim_boundary_scan_2026-06-19.json` | Confirms current front-door docs resolve to v3.0.2 and do not positively publish blocked V4 claims. |
| Source-tree runtime story | `docs/engineering/rtdl_v4_0_source_tree_runtime_story_2026-06-19.md` | Documents the V4 M1 source-tree runtime path and keeps package, PyPI, wheel, and stable SDK wording blocked. |

Current reproducibility gate:

```bash
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_active
```

Latest Linux validation on `192.168.1.20` for source-tree head
`22bf64678858b8ad7606f32428d918f511f5f179`:

- source-tree doctor with V4 active checks: pass;
- `v4_active`: 59 tests, pass;
- front-door claim-boundary scan: pass;
- `make build-optix`: pass;
- DLPack capsule probe: pass;
- `git diff --check`: pass.
- worktree clean.

Clean cross-stream prepare/query event-wait evidence commit:
`48ce1f9725613f746cea9ba0de438ae0ee830ca3`. On `192.168.1.20`,
`make build-optix`, `v4_active`, the refreshed stream-ordering probe,
front-door claim scan, JSON validation, `git diff --check`, and clean worktree
status all passed.

Native build and route probes were also validated on the preceding M1
implementation-bearing commits: `make build-optix`, same-stream ordering,
Numba CUDA Array Interface smoke, Numba M1 `DeviceNDArray` fixed-radius route
probe, DLPack bridge wrapper smoke, and `git diff --check` all passed there.

Current source-tree `v4_active` gate after the release-candidate blocker,
front-door claim-scan, Numba route-evidence guards, source-tree runtime story
guard, fixed-radius cross-stream prepare/query event-wait guard, and DLPack
capsule report guards: 61 tests, pass locally.

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
- "Different nonzero prepare/query CUDA streams are ordered by a native prepare-ready event for the fixed-radius M1 route."
- "A CuPy-backed DLPack-only wrapper smoke exercises the generic DLPack adapter."
- "The fixed-radius M1 route has experimental legacy DLPack capsule evidence with stream argument propagation and pointer echo."
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
- Full Numba partner surface, PyTorch, arbitrary framework-neutral DLPack, or
  full DLPack route support.

## Current Claim Flags

| Claim | Status |
| --- | --- |
| Current release/front-door promotion | blocked |
| Stable SDK/package install | blocked |
| Public true-zero-copy | blocked |
| Async/nonblocking completion | blocked |
| Same-stream ordering | experimental M1 evidence |
| Fixed-radius M1 prepare/query event-wait | experimental M1 evidence |
| General cross-stream event waits | blocked |
| Public speedup | blocked |
| RTX/RT-core speedup | blocked |
| CuPy route evidence | experimental M1 evidence |
| Numba `DeviceNDArray` via CUDA Array Interface | experimental M1 evidence |
| Bounded Numba M1 `DeviceNDArray` fixed-radius route | experimental M1 evidence |
| DLPack bridge wrapper over CuPy-owned arrays | experimental M1 evidence |
| Fixed-radius M1 legacy DLPack capsule route | experimental M1 evidence |
| Full arbitrary Numba partner surface | blocked |
| PyTorch route evidence | not yet present |
| Full DLPack capsule/framework route evidence | blocked |

PyTorch preflight on `192.168.1.20`, 2026-06-19: blocked by runtime
availability. The host has CuPy/Numba but no `torch` module; there is no
passwordless sudo, `python3.12-venv` is unavailable, and the attempted user-site
Torch dry-run was unbounded and stopped. No PyTorch route support wording is
authorized until an actual CUDA tensor smoke passes.

Cross-stream prepare/query event-wait preflight on `192.168.1.20`,
2026-06-19: passing with boundaries for the fixed-radius M1 route. The native
prepared handle owns a CUDA prepare-ready event, records it after
prepare-dependent CUDA/OptiX work, and waits on it from a different query
stream before launching query work. Native prepare and query calls still
synchronize before returning. This authorizes only narrow fixed-radius M1
prepare/query ordering across distinct nonzero CUDA streams; it does not
authorize async execution, public event-handle ownership, full external stream
ownership, or general cross-stream behavior outside this route.

Numba M1 `DeviceNDArray` fixed-radius route probe on `192.168.1.20`,
2026-06-19: passing with boundaries. The route has Numba `DeviceNDArray`
parity cases, pointer identity checks through the V4 plan and native pointer
echo, caller-owned output columns, a same-stream Numba consumer checksum, and
prepared-handle reuse evidence while the caller keeps search columns alive.
This authorizes bounded M1 `DeviceNDArray` fixed-radius route wording only; it
does not authorize arbitrary Numba program acceleration or a broad
full-partner-surface claim.

DLPack capsule fixed-radius route probe on `192.168.1.20`, 2026-06-19:
passing with boundaries. The route has real legacy DLPack capsule intake,
stream argument propagation, plan pointer identity, native pointer echo,
output correctness, and Python consume-once/deleter-once guards. This
authorizes only narrow fixed-radius M1 legacy DLPack capsule wording; it does
not authorize arbitrary framework-neutral DLPack, PyTorch, async completion,
public true-zero-copy, or speedup wording.

Source-tree runtime story preflight, 2026-06-19: passing with boundaries. The
V4 M1 source-tree flow is documented and source-tree-doctor checked on Windows
and Linux; Linux has CuPy, Numba, and the OptiX library after `make build-optix`.
This authorizes source-tree runtime wording only. It does not authorize package
install, PyPI, wheel, stable SDK, or generated binding wording.

RTX/RT-core speed preflight, 2026-06-19: still blocked by hardware access. The
available Linux GPU host is a GTX 1070 and can validate CUDA/OptiX execution and
Python GPU interop, but it is not RTX-class evidence. The provided RTX pod SSH
endpoint `root@157.157.221.29:22234` returned `Permission denied
(publickey,password)` with the available key, so RT-core or RTX speedup wording
remains unauthorized.

## Next Gates

1. Keep the M1 route reproducible on current head.
2. Keep the fixed-radius M1 cross-stream prepare/query event-wait evidence fresh while async and full external-stream ownership remain blocked.
3. Add PyTorch or broader framework-neutral DLPack evidence before saying those surfaces are validated.
4. Use RTX-class hardware before any RT-core speed discussion.
5. Keep the release-candidate blocker manifest current while `v4_release_candidate` remains absent from the passing test matrix.
6. Only after an M8 release-candidate packet exists and the blocker manifest is closed, expose a `v4_release_candidate` gate and reconsider whether V4 can become the current front door.
