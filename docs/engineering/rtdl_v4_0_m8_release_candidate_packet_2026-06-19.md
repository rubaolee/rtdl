# RTDL V4.0 M8 Release-Candidate Evidence Packet

Status: review-ready M8 evidence packet, not release approval.

Date: 2026-06-19

Implementation evidence baseline:
`bbc43984b74dee7d52c059b295c5eaade0813096`

First M8 packet/gate commit:
`0273d4cba5e38afee099573b0ac47f2f883c1067`

External review request commit:
`eba6f4b6e49152d8da4e545477a1cb125f6bab43`

Post-review action validation commit:
`66e6529859a1bac63ce2a72527dc5942e301143d`

Package/runtime hygiene validation commit:
`1ad0a1437b38a3a043948ee96afc216dffe844a1`

Next-step external-review consensus guard commit:
`3e22e03bd4fe70454a7b5a11b30c7990c4dfff9d`

Final release-candidate commit: not assigned. Release-candidate readiness is
still false.

## Verdict

V4.0 is ready for critical review as an experimental source-tree candidate for
the OptiX-backed Python GPU operator direction.

It is not the current user release. The current user release remains `v3.0.2`.
This packet does not authorize a front-door switch, package-install wording,
stable SDK wording, public true-zero-copy wording, async wording, public
speedup wording, or RTX/RT-core speedup wording.

## V4.0 Candidate Scope

V4.0 is scoped to Python actors using RTDL as an OptiX-backed GPU operator
lane.

The first candidate product route is:

`fixed_radius_count_threshold_2d`

The route accepts caller-owned CUDA point columns, prepares an OptiX
fixed-radius count/threshold index, and writes fixed-size caller-owned CUDA
output columns:

- `query_ids`;
- `neighbor_counts`;
- `threshold_flags`.

This route is fixed-size one-output-row-per-query. It is not variable-length
neighbor enumeration.

## Implemented Python Surface

The Python entry points are:

- `rtdsl.prepare_v4_fixed_radius_count_threshold_2d`
- `rtdsl.run_v4_fixed_radius_count_threshold_2d`

Evidence-backed input paths:

- CuPy CUDA arrays;
- Numba `DeviceNDArray` through CUDA Array Interface;
- legacy DLPack capsules for the fixed-radius M1 route;
- PyTorch detached contiguous CUDA tensors.

Evidence-backed stream behavior:

- nonzero caller CUDA streams propagate through prepare and query;
- same-stream producer -> RTDL -> consumer ordering is validated;
- different nonzero prepare/query streams are ordered for the fixed-radius M1
  route by a native prepare-ready event;
- native prepare and query calls still synchronize before returning;
- async/nonblocking completion is not claimed.

Evidence-backed output behavior:

- output columns are caller-owned CUDA arrays/tensors;
- output length is one row per query;
- unsupported output shape, dtype, missing-column, and extra-column cases fail
  closed in the compatibility probes.

## Rejected Or Blocked Cases

The current compatibility evidence rejects:

- CPU tensors for the PyTorch route;
- wrong dtypes;
- bad rank;
- non-contiguous PyTorch sliced views;
- mismatched input lengths;
- bad output lengths;
- missing output columns;
- extra output columns;
- grad-enabled PyTorch input or output tensors.

The current evidence does not validate:

- arbitrary PyTorch tensor layouts beyond the matrix;
- autograd integration;
- graph/compiler integration;
- arbitrary Numba program acceleration;
- arbitrary framework-neutral DLPack support;
- async completion;
- public true-zero-copy;
- public speedup;
- RTX/RT-core speedup;
- package install, PyPI, wheel, or stable SDK usage;
- public multi-language C ABI or non-Python host embedding.

## Evidence Ledger

| Evidence | Path | Status |
| --- | --- | --- |
| M1 experimental status | `docs/engineering/rtdl_v4_0_m1_experimental_status_2026-06-19.md` | Current status packet; V4 remains experimental and v3.0.2 remains current release. |
| Blocker manifest | `docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json` | Machine-readable release blockers and closed evidence. |
| Source-tree runtime story | `docs/engineering/rtdl_v4_0_source_tree_runtime_story_2026-06-19.md` | Source-tree runtime only; package/PyPI/wheel/SDK claims blocked. |
| Source-tree runtime preflight | `docs/reports/v4_0_source_tree_runtime_preflight_2026-06-19.json` | Linux required-runtime preflight passed for checkout import, CuPy, Numba, PyTorch, and OptiX. |
| Editable install hygiene probe | `docs/reports/v4_0_editable_install_runtime_probe_2026-06-19.json` | Linux editable source-tree install hygiene with V4 GPU smoke; not package/PyPI/wheel/stable SDK evidence. |
| Front-door claim scan | `docs/reports/v4_0_current_front_door_claim_boundary_scan_2026-06-19.json` | Pass; current front door remains v3.0.2 and blocked V4 claims are not published positively. |
| CuPy stream smoke | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_smoke_2026-06-19.json` | Pointer identity, stream propagation, output correctness. |
| CuPy parity matrix | `docs/reports/v4_0_m1_fixed_radius_cupy_parity_matrix_2026-06-19.json` | Positive and fail-closed parity cases. |
| CuPy no-host-stage probe | `docs/reports/v4_0_m1_fixed_radius_cupy_no_host_stage_probe_2026-06-19.json` | Named-column no-host-stage evidence; not public true-zero-copy. |
| CuPy stream ordering | `docs/reports/v4_0_m1_fixed_radius_cupy_stream_ordering_probe_2026-06-19.json` | Same-stream and fixed-radius prepare/query event-wait evidence. |
| CuPy benchmark probe | `docs/reports/v4_0_m1_fixed_radius_cupy_benchmark_probe_2026-06-19.json` | Route timing smoke only; no public speedup wording. |
| Numba CUDA Array Interface smoke | `docs/reports/v4_0_m1_fixed_radius_numba_cuda_array_interface_smoke_2026-06-19.json` | Numba smoke path evidence. |
| Numba M1 partner probe | `docs/reports/v4_0_m1_fixed_radius_numba_partner_surface_probe_2026-06-19.json` | Bounded M1 `DeviceNDArray` route evidence; full Numba surface blocked. |
| DLPack bridge smoke | `docs/reports/v4_0_m1_fixed_radius_dlpack_bridge_smoke_2026-06-19.json` | CuPy-backed DLPack-only wrapper smoke. |
| DLPack capsule probe | `docs/reports/v4_0_m1_fixed_radius_dlpack_capsule_probe_2026-06-19.json` | Narrow legacy capsule intake, stream, pointer, consume-once, deleter-once evidence. |
| PyTorch CUDA tensor probe | `docs/reports/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe_2026-06-19.json` | PyTorch route compatibility matrix for the fixed-radius M1 operator. |
| Active ABI slice | `docs/engineering/rtdl_v4_0_active_abi_slice_2026-06-19.md` | Phase 2 substrate evidence, not product headline. |
| Active ABI layout audit | `docs/reports/v4_0_active_abi_layout_audit_2026-06-19.json` | Experimental C ABI layout audit. |
| M8 next-step consensus | `docs/reviews/codex_v4_after_runtime_preflight_m8_next_step_2ai_consensus_2026-06-19.md` | 2-AI decision to assemble this M8 packet before broad feature expansion. |
| M8 internal critical review | `docs/reviews/codex_v4_m8_internal_2ai_critical_review_2026-06-19.md` | 2-AI review accepts this as a baseline and rejects release-candidate readiness today. |
| Package/runtime tie-breaker | `docs/reviews/codex_v4_package_runtime_tiebreaker_2026-06-19.md` | Requires editable-install hygiene evidence while keeping package/PyPI/wheel claims blocked. |

## Validation Summary

Linux validation on `192.168.1.20` for the implementation evidence baseline
`bbc43984b74dee7d52c059b295c5eaade0813096`, first M8 packet/gate smoke at
`0273d4cba5e38afee099573b0ac47f2f883c1067`, and post-review action validation
at `66e6529859a1bac63ce2a72527dc5942e301143d`:

- `make build-optix`: pass;
- `scripts/run_test_matrix.py --group v4_active`: 71 tests, pass;
- `scripts/run_test_matrix.py --group v4_release_candidate`: 71 tests, pass
  as a non-authorizing review gate;
- `scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime`:
  pass;
- `scripts/v4_0_current_front_door_claim_boundary_scan.py`: pass;
- blocker manifest JSON parse: pass;
- source-tree runtime preflight JSON parse: pass;
- `git diff --check`: pass;
- worktree clean.

Package/runtime hygiene validation on `192.168.1.20` for source-tree head
`1ad0a1437b38a3a043948ee96afc216dffe844a1`:

- `make build-optix`: pass;
- `scripts/v4_0_source_tree_runtime_preflight.py --require-v4-gpu-runtime`:
  pass;
- `scripts/v4_0_editable_install_runtime_probe.py --system-site-packages
  --run-v4-smoke`: pass;
- the editable probe used a fresh venv from a working directory outside the
  repository with `PYTHONPATH` unset, falling back to
  `venv --without-pip` plus `pip --python` because the host lacks ensurepip;
- the V4 smoke loaded `rtdsl` from the editable checkout, found
  `build/librtdl_optix.so` under the checkout, and produced the expected
  `query_ids`, `neighbor_counts`, and `threshold_flags`;
- `git diff --check`: pass;
- worktree clean.

No-expansion external-review guard validation on `192.168.1.20` for source-tree
head `3e22e03bd4fe70454a7b5a11b30c7990c4dfff9d`:

- `scripts/run_test_matrix.py --group v4_active`: 73 tests, pass;
- `scripts/run_test_matrix.py --group v4_release_candidate`: 73 tests, pass
  as a non-authorizing review gate;
- `git diff --check`: pass;
- worktree clean.

The route-specific JSON reports above preserve the earlier CuPy, Numba,
DLPack, and PyTorch probe evidence. This packet binds that evidence into one
review surface; it does not broaden those route claims.

## Non-Authorizations

This M8 packet does not authorize:

- V4.0 as the current release;
- V4.0 as the default user front door;
- package install, PyPI, wheel, or stable SDK wording;
- generated binding package wording;
- public multi-language C ABI release wording;
- public true-zero-copy, end-to-end zero-copy, no-copy, or no-H2D-copy wording;
- async or nonblocking completion wording;
- public speedup, RTX speedup, RT-core speedup, or "RTDL is faster" wording;
- full PyTorch, full Numba, or full framework-neutral DLPack support;
- non-Python host embedding as a V4.0 deliverable.

## Open Release Gates

| Gate | Current state |
| --- | --- |
| External M8 critical review | Open; this packet is the review input. |
| Package/runtime decision | Source-tree runtime and editable-install hygiene are validated; package/PyPI/wheel/stable SDK claims remain blocked. |
| Front-door docs switch | Blocked until release approval and explicit user action. |
| Public true-zero-copy | Blocked until end-to-end copy evidence exists. |
| Async completion | Blocked until lifetime and event contracts are implemented and tested. |
| Public speedup/RTX speedup | Blocked until RTX-class evidence and accepted benchmark matrix exist. |
| Full PyTorch/Numba/DLPack surfaces | Blocked beyond exact M1 route evidence. |
| Stable SDK/C ABI | Blocked; C ABI remains Phase 2 substrate and V4.x path. |

## Review Request

Please critically review this packet and the linked evidence.

Questions for reviewers:

1. Is V4.0's candidate scope honest: OptiX-backed Python GPU operator, exact
   fixed-radius M1 route, source-tree runtime only?
2. Is the evidence sufficient to call this an experimental V4.0 candidate for
   review, without switching the user front door?
3. Are any claims still too broad, especially around zero-copy, streams,
   DLPack, PyTorch, package/runtime, or RT-core performance?
4. Are the accepted and rejected device-array cases clear enough for users?
5. Should V4.0 remain source-tree experimental, or must a clean package/editable
   install flow become a release blocker?
6. What specific gate must close before V4.0 can become the current user
   release?

Requested output:

- P0 blockers;
- P1 risks;
- P2 clarity/polish issues;
- forbidden wording;
- required additional tests or evidence;
- accept/reject decision for using this as the M8 review baseline.
