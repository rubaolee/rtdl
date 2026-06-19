# RTDL V4.0 M1 Experimental Status

Status: experimental engineering evidence, not current release.
Date: 2026-06-19.
Latest validated source-tree head: `d1b84b170756bb48df4b4e0766cfa5dd9341aaa0`.
Latest validated source-tree tree: `e2188f2fd983b2c1afb5f0e34f84773d573b2bb4`.

This packet summarizes the current V4.0 M1 state after the fixed-radius
Python CUDA device-array route gained CuPy, Numba, PyTorch, and bounded legacy
DLPack evidence. It is an engineering status packet, not a release packet,
stable SDK promise, package-install promise, public speedup claim, or public
true-zero-copy claim.

## Release Position

V4.0 is not the current user release/front door.

The current source-tree release remains `v3.0.2`. The V4.0 M1 work is an
active engineering preview for the OptiX-backed Python GPU operator direction.

This status follows the 2-AI release-positioning consensus:

`docs/reviews/codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md`

## M1 Product Route

Route: `fixed_radius_count_threshold_2d`

Python API:

- `rtdsl.prepare_v4_fixed_radius_count_threshold_2d`
- `rtdsl.run_v4_fixed_radius_count_threshold_2d`

Implemented contract:

- host program is Python with evidence-backed CuPy, Numba, or PyTorch CUDA
  device arrays;
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
- a fixed-radius M1 PyTorch CUDA tensor route has pointer, stream, output,
  detached tensor acceptance, fail-closed compatibility, and grad-enabled
  tensor rejection evidence;
- arbitrary framework-neutral DLPack and full PyTorch partner-surface wording
  remain blocked.

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
| DLPack capsule probe | `docs/reports/v4_0_m1_fixed_radius_dlpack_capsule_probe_2026-06-19.json` | Authorizes narrow fixed-radius M1 legacy DLPack capsule wording for stream argument propagation, pointer identity, native pointer echo, output correctness, and consume-once/deleter-once guards; does not authorize arbitrary framework-neutral DLPack. |
| PyTorch CUDA tensor probe | `docs/reports/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe_2026-06-19.json` | Authorizes exact fixed-radius M1 PyTorch CUDA tensor route wording for pointer identity, native pointer echo, same-stream checksum, direct `torch.cuda.Stream` objects, distinct prepare/query stream ordering, caller-owned outputs, detached tensor acceptance, and fail-closed compatibility cases; does not authorize a full PyTorch partner surface. |
| True-zero-copy wording consensus | `docs/reviews/codex_v4_m1_true_zero_copy_wording_consensus_2026-06-19.md` | Keeps public true-zero-copy wording blocked. |
| Release-positioning consensus | `docs/reviews/codex_v4_m1_release_positioning_2ai_consensus_2026-06-19.md` | Keeps v3.0.2 as current release and V4 as experimental M1 evidence. |
| Release-candidate blocker manifest | `docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json` | Exposes `v4_release_candidate` only as a non-authorizing M8 review gate; release remains blocked. |
| Front-door claim scan | `docs/reports/v4_0_current_front_door_claim_boundary_scan_2026-06-19.json` | Confirms current front-door docs resolve to v3.0.2 and do not positively publish blocked V4 claims. |
| Source-tree runtime story | `docs/engineering/rtdl_v4_0_source_tree_runtime_story_2026-06-19.md` | Documents the V4 M1 source-tree runtime path and keeps package, PyPI, wheel, and stable SDK wording blocked. |
| Source-tree runtime preflight | `docs/reports/v4_0_source_tree_runtime_preflight_2026-06-19.json` | Linux required-runtime preflight validates checkout import, source-tree package identity, CuPy, Numba, PyTorch, OptiX library, and non-package claim boundaries. |

Current reproducibility gate:

```bash
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_active
```

Latest Linux validation on `192.168.1.20` for source-tree head
`d1b84b170756bb48df4b4e0766cfa5dd9341aaa0`:

- source-tree doctor with V4 active checks: pass;
- source-tree runtime preflight with required V4 GPU runtime: pass;
- `v4_active`: 71 tests, pass;
- front-door claim-boundary scan: pass;
- `make build-optix`: pass;
- DLPack capsule probe: pass;
- PyTorch CUDA tensor probe: pass;
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
guard, source-tree runtime preflight guard, fixed-radius cross-stream
prepare/query event-wait guard, and DLPack capsule report guards, PyTorch route
report guards, PyTorch compatibility guards, and PyTorch boundary guards:
71 tests, pass locally and on Linux.

## Release-Candidate Boundary

The source tree exposes `v4_release_candidate` as a non-authorizing M8 review
gate. Passing it means the current M8 evidence packet, V4 active tests, and
claim boundaries are internally coherent. It does not mean V4.0 is the current
release or user front door.

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
- "The fixed-radius M1 route has experimental PyTorch CUDA tensor evidence with pointer echo, same-stream checksum, direct torch stream objects, distinct prepare/query stream ordering, caller-owned outputs, detached tensor acceptance, and fail-closed compatibility cases."
- "Raw route-scoped timing probe exists; it does not authorize public speedup wording."

## Blocked Wording

- V4.0 is the current release.
- Stable V4 SDK.
- Package install, PyPI, or wheel support.
- Generated bindings or public multi-language C ABI release.
- True zero-copy, end-to-end zero-copy, no copies, no staging, or no H2D copies.
- Async, nonblocking, or returns before GPU work completes.
- General cross-stream event wait support beyond the fixed-radius M1
  prepare/query event-wait contract.
- RT-core speedup, RTX speedup, RTDL is faster, or broad performance claims.
- Full Numba or PyTorch partner surface, arbitrary framework-neutral DLPack, or
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
| Fixed-radius M1 PyTorch CUDA tensor route and compatibility matrix | experimental M1 evidence |
| Full arbitrary PyTorch partner surface | blocked |
| Full DLPack capsule/framework route evidence | blocked |

PyTorch fixed-radius M1 CUDA tensor route probe on `192.168.1.20`,
2026-06-19: passing with boundaries. The route has PyTorch CUDA tensor pointer
identity, native pointer echo, same-stream checksum, direct `torch.cuda.Stream`
object handling, distinct prepare/query stream ordering, caller-owned output
columns, detached tensor acceptance, and fail-closed cases for CPU tensors,
wrong dtypes, rank, non-contiguous sliced views, mismatched lengths,
output-contract errors, missing/extra columns, and grad-enabled input/output
tensors. This authorizes exact fixed-radius M1 PyTorch CUDA tensor route
wording only; it does not authorize arbitrary PyTorch tensor layouts beyond the
matrix, autograd integration, graph/compiler integration, broad PyTorch program
acceleration, async completion, public true-zero-copy, or speedup wording.

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
not authorize arbitrary framework-neutral DLPack, async completion, public
true-zero-copy, or speedup wording.

Source-tree runtime story preflight, 2026-06-19: passing with boundaries. The
V4 M1 source-tree flow is documented and source-tree-doctor checked on Windows
and Linux; Linux has CuPy, Numba, PyTorch, and the OptiX library after
`make build-optix`. The tracked runtime preflight report
`docs/reports/v4_0_source_tree_runtime_preflight_2026-06-19.json` records
required Linux V4 GPU runtime checks passing on
`d1b84b170756bb48df4b4e0766cfa5dd9341aaa0`.
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
3. Broaden PyTorch or framework-neutral DLPack evidence before saying those full surfaces are validated.
4. Use RTX-class hardware before any RT-core speed discussion.
5. Keep the release-candidate blocker manifest current while `v4_release_candidate` remains a non-authorizing review gate.
6. Only after external review and explicit release approval, reconsider whether V4 can become the current front door.
