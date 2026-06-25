# Call For Review: V4 Forward Goals `goal4615`-`goal4623`

Date: 2026-06-24
Author: Codex
Status: goals proposal for Claude review before implementation

This document defines the next V4 work sequence using the project-continuous
goal numbering. The previous highest project goal is `goal4614`, so this V4
sequence starts at `goal4615`.

No implementation is authorized by this document. Work starts only after
Claude accepts this goals plan, or after amendments requested by Claude are
applied and accepted.

## Current V4 Ground Truth

The active V4 design is:

- `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`

V4.0 is the Python GPU-array RT-core lane with fused Tier-2 generic operators
and a constrained Tier-3 spike path. It is not the old C ABI / embedding /
multi-language host plan. It must not expose raw OptiX callbacks, must not add
app-identity native kernels, and must not claim broad speedups or whole-app
speedups without measured evidence.

Current measured catalog surfaces:

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_closest_hit_grouped_argmin_3d_device_arrays`
- `v4_ray_triangle_any_hit_flags_2d_device_arrays`

Current candidate surfaces with POD evidence:

- `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- `v4_point_group_nearest_witness_2d_device_arrays`

Important current reviews:

- `future/v4/reviews/claude_v4_primitive_grouped_i64_candidate_review_2026-06-24.raw.md`
- `future/v4/reviews/claude_v4_point_group_candidate_amendment_closure_review_2026-06-24.raw.md`

Known danger:

- A 3D fixed-radius count-threshold expansion is attractive, but the current
  3D native route appears to be prepared-search plus host query points with
  device output columns, not a full Python GPU-array query surface. It must not
  be marketed or wrapped as `*_device_arrays` until the native device-query
  path is real.

## Global Rules For These Goals

1. Every completed goal requires a recorded 3-AI completion consensus before
   it can be marked complete. Preferred seats are Codex, Claude, and
   Antigravity. If a seat is unavailable, the missing review may be recorded as
   review debt, but the goal must not be represented as fully complete.
2. Claude review is required before major decisions, candidate promotion, new
   native surface implementation, Tier-3 spike execution, or release wording.
3. Do not open V4 embedding/C-ABI/non-Python-host work in this sequence.
4. Do not add app-specific native kernels. Allowed native fusion is only for
   generic continuation operators such as count, threshold, any-hit flag,
   grouped sum/min/max/count, argmin/argmax, bounded collect/top-k, or nearest
   witness.
5. Do not call a path "true zero-copy" unless a separate review explicitly
   authorizes that wording. The current safe wording is direct device-array
   handoff or direct device read/write where the metadata proves it.
6. POD time is used only for gates that need RTX/OptiX evidence. Local work
   should continue while reviews or POD jobs are pending.
7. A green unit test is not a release claim. Evidence must state scope,
   partner, hardware, ABI, correctness parity, and non-authorization.

## Goal-Level Decision Audit For This Plan

1. Am I being foolish by writing a goals plan instead of coding immediately?
   No. The user explicitly required goals first, continuous numbering, then
   Claude review, then work.
2. What action would make this foolish?
   Starting native implementation or promotion edits before Claude reviews the
   sequence would repeat the old failure mode: motion before agreed gates.
3. Is there an alternate path that avoids getting stuck in process?
   Yes. Keep this document short enough to review once, then use it as the
   single control plane. Do not generate per-microstep review packages.
4. Can I solve the problem differently?
   Yes. If Claude rejects a goal as process churn, collapse it into the next
   implementation goal and preserve only the evidence gate.

## `goal4615` — Freeze The V4 Forward Goals And Get Claude Consensus

Purpose:

- Establish the next V4 sequence before new implementation.
- Confirm continuous goal numbering after `goal4614`.
- Get Claude to identify missing gates, wrong ordering, or hidden scope creep.

Tasks:

- Write this goals document.
- Ask Claude to review it as the first external reviewer.
- Apply required amendments if Claude blocks the plan.

Exit gate:

- Claude verdict is either accept, or accept with amendments that are applied.
- The accepted plan is recorded under `future/v4/reviews/`.

Forbidden:

- No implementation.
- No catalog promotion.
- No release wording.

Completion review:

- Needs 3-AI completion consensus to mark `goal4615` complete. If only Claude
  is available now, record Antigravity/third-seat debt and do not overclaim
  full completion.

## `goal4616` — Consolidate Current V4 State And Review Debt

Purpose:

- Turn the current V4 worktree into an auditable state before further changes.
- Prevent old V3/V4 churn from hiding the actual V4 surface truth.

Tasks:

- Update or create a V4 status ledger that records:
  - three measured surfaces
  - two candidate surfaces
  - point-group amendment closure
  - grouped-i64 required amendments R1-R4
  - known wording debt around `*_true_zero_copy_authorized`
  - Antigravity/third-seat review debt
- Run local non-GPU validation for the status surface.
- Do not change measured/candidate classification.

Likely paths:

- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/v2_primitives_to_v4_tier2_inventory_2026-06-24.md`
- `future/v4/reviews/`

Exit gate:

- Status ledger exists and matches code/catalog evidence.
- Dry-run catalog gate and local unit tests pass.
- The status ledger must not introduce claim-status changes that are not
  already authorized by existing code, evidence, and prior reviews.

Forbidden:

- No candidate promotion.
- No new native code, except comment-only or string-constant changes in
  existing native files, or a test compilation probe that does not add a new
  native API surface.

Completion review:

- 3-AI completion consensus required.

## `goal4617` — Grouped-I64 Candidate Promotion Decision Package

Purpose:

- Decide whether `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
  is ready to move from candidate to measured catalog, or remains candidate.

Tasks:

- Address Claude R1-R4 from the grouped-i64 candidate review:
  - include the surface in the GPU-mode catalog gate when promotion is proposed
  - update measured-partner status atomically only if promotion is authorized
  - state OptiX ABI scope, especially OptiX 8.0 vs 9.1
  - update measured-surface count from 3 to 4 only if promotion is authorized
- Either expand group-width coverage or explicitly scope the validated width.
- Run required local tests and POD GPU gate if promotion is proposed.
- Write a promotion-decision packet.

Likely paths:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_ray_triangle.py`
- `scripts/v4_catalog_regression_gate.py`
- `tests/v4_catalog_regression_gate_test.py`
- `future/v4/evidence/`
- `future/v4/reviews/`

Exit gate:

- External reviewers either authorize promotion or require keeping candidate
  status.
- Claude review is required before a promotion decision is finalized.
- If promoted, the catalog and planner say measured only for validated Torch
  scope and CuPy remains declared-unmeasured.
- If not promoted, the catalog stays candidate and the reason is recorded.

Forbidden:

- No broad V4 or whole-app speedup claim.
- No true-zero-copy claim.

Completion review:

- 3-AI completion consensus required.

## `goal4618` — Point-Group Candidate Promotion Decision Package

Purpose:

- Decide whether `v4_point_group_nearest_witness_2d_device_arrays` is ready to
  move from candidate to measured catalog after Claude accepted A1-A3 closure.

Tasks:

- Build a separate promotion packet; do not treat amendment closure as
  automatic promotion.
- Reconfirm mixed fixture correctness, no-hit sentinel, nonzero distances, and
  same-contract ratio scope.
- Decide whether additional edge coverage is needed before measured catalog:
  empty groups, non-axis no-hit rows, or larger row distributions.
- Run include-candidates or promotion GPU gate on POD if promotion is proposed.

Likely paths:

- `src/rtdsl/v4_point_group.py`
- `src/rtdsl/v4_operator_catalog.py`
- `scripts/v4_catalog_regression_gate.py`
- `tests/v4_point_group_device_array_api_test.py`
- `future/v4/evidence/`
- `future/v4/reviews/`

Exit gate:

- External reviewers either authorize measured-catalog promotion or require
  keeping candidate status.
- Claude review is required before a promotion decision is finalized.
- Any promotion preserves partner scope: Torch measured only if authorized,
  CuPy declared-unmeasured.

Forbidden:

- No release shortcut from amendment closure.
- No true-zero-copy claim.

Completion review:

- 3-AI completion consensus required.

## `goal4619` — 3D Fixed-Radius Device-Array Feasibility Gate

Purpose:

- Determine whether the 3D fixed-radius count-threshold family can honestly
  become a V4 Python GPU-array Tier-2 surface, or must remain a narrower
  prepared-search / device-output candidate.

Tasks:

- Audit native symbols and Python routing for 3D fixed-radius:
  - search point device columns
  - query point device columns
  - output device columns
  - no host query-row materialization in the measured hot path
- If the device-query route is missing, write a no-go/required-native-work
  record instead of wrapping it misleadingly.
- If feasible, produce a minimal native compile probe plan for a real 3D
  device-column query route.

Likely paths:

- `src/rtdsl/v4_fixed_radius.py`
- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_cuda_helpers.cu`

Exit gate:

- One of:
  - Go: exact native/Python symbols needed for true device-array 3D route are
    identified and the implementation risk is bounded.
  - No-Go: route is not currently honest as a V4 device-array surface and is
    deferred or reframed.
- A Go verdict must be submitted to Claude review before `goal4620`
  implementation begins.
- A No-Go verdict requires Claude review of the fallback candidate before
  `goal4620` begins.

Forbidden:

- No marketing of existing 3D host-query route as V4 device-array input.
- No code implementation before the feasibility verdict is reviewed.

Completion review:

- 3-AI completion consensus required.

## `goal4620` — Implement One New Tier-2 Surface Only If `goal4619` Is Go

Purpose:

- Add a new V4 Tier-2 fused generic operator surface only after the feasibility
  gate proves the route is honest.

Primary route:

- Implement `v4_fixed_radius_count_threshold_3d_device_arrays` only if
  `goal4619` is Go.

Fallback route:

- If `goal4619` is No-Go, select the next candidate from the inventory by
  Claude review before implementation begins:
  - ranked fixed-radius summary/top-k
  - aggregate weighted-vector sum as a generic weighted-vector operator
  - another generic app-name-free fused operator

Tasks:

- Add native route only for generic operator semantics.
- Add Python front door, claim boundary, tests, example, and POD evidence.
- Compare against the older route that the new surface replaces.
- Record correctness parity and direct device-array metadata.

Exit gate:

- Candidate-level POD evidence exists with correctness parity.
- Candidate is not promoted until a separate decision.

Forbidden:

- No app-specific kernel.
- No raw callback exposure.
- No measured-catalog promotion inside this goal unless the separate promotion
  review explicitly authorizes it.

Completion review:

- 3-AI completion consensus required.

## `goal4621` — Tier-2 Catalog Hardening

Purpose:

- Make the V4 operator catalog and planner hard to misread.

Tasks:

- Ensure measured vs candidate vs declared-unmeasured status is explicit for
  every surface.
- Normalize claim-boundary metadata:
  - direct device read/write fields
  - `true_zero_copy_authorized`
  - partner claim status
  - release and broad-speedup non-authorization fields
- Ensure examples and README show only current, clean V4 surfaces.
- Ensure old V3/V4 or history material is not presented as user front-door
  guidance.

Likely paths:

- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`
- `scripts/v4_catalog_regression_gate.py`
- `future/v4/examples/`

Exit gate:

- Local tests and catalog regression gate pass.
- A reviewer can tell which surfaces are measured, candidate, or deferred
  without reading history files.

Forbidden:

- No performance claim broadening.

Completion review:

- 3-AI completion consensus required.

## `goal4622` — Tier-3 Callback Spike Protocol, Not Support

Purpose:

- Define, but not yet sell, the constrained Tier-3 Numba/PTX-to-OptiX spike for
  complex user callbacks that cannot be expressed as Tier-2 operators.

Tasks:

- Write a falsifiable spike protocol:
  - accepted callback shape: scalar per-hit reduce only
  - rejected shapes: shared mutation, dynamic allocation, variable-length
    output, recursive/spawned action logic
  - pinned toolchain assumptions
  - expected overhead measurements
  - kill criteria
  - kill criteria must be measurable and fixed before any spike implementation
    runs, including at minimum:
    - an overhead ceiling
    - a compile-reliability floor for the pinned toolchain
    - a correctness-parity requirement
- Keep planner behavior conservative: accepted only as spike/deferred, not
  supported V4.0 feature.

Likely paths:

- `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`
- `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- `src/rtdsl/v4_operator_catalog.py`
- `tests/v4_operator_catalog_test.py`

Exit gate:

- Protocol is reviewed and either authorized for a later spike or deferred.

Forbidden:

- No implementation unless separately authorized after review.
- No raw OptiX callback support claim.

Completion review:

- 3-AI completion consensus required.

## `goal4623` — V4 Release Candidate Or Development-State Decision

Purpose:

- Decide whether current V4 is a release candidate, or remains a development
  catalog with measured/candidate surfaces.

Tasks:

- Run the final V4 catalog gate on the validated hardware.
- Include all measured surfaces and, if requested, candidate examples clearly
  labeled as candidates.
- Ensure docs, examples, tutorials, and front page are clean for users.
- Get external 3-AI review for release wording, surface status, and performance
  scope.

Exit gate:

- One of:
  - Release candidate authorized with exact measured surface list and exact
    partner/hardware/ABI scope.
  - Development-state documentation disclosure authorized with no
    release-speedup wording.
  - No release; continue build.

Forbidden:

- No broad V4 speedup claim.
- No whole-app benchmark claim unless a separate all-app benchmark protocol has
  run and passed.
- No embedding/C-ABI/non-Python host claim.

Completion review:

- 3-AI completion consensus required.

## Review Questions For Claude

1. Is the `goal4615`-`goal4623` ordering correct, or does any goal need to move?
2. Does the plan avoid the old failure mode of process churn while still
   respecting the user's review/consensus requirements?
3. Are grouped-i64 and point-group promotion decisions correctly separated from
   their candidate evidence and amendment closure?
4. Is `goal4619` the right guard against falsely wrapping the existing 3D
   fixed-radius host-query route as a V4 device-array surface?
5. Are the Tier-3 constraints strict enough for complex user callbacks?
6. Are any goals missing correctness parity, POD evidence, claim boundary, or
   non-authorization gates?
7. What amendments are required before implementation may begin?

## Non-Authorization

This goals document does not authorize:

- V4 release
- measured-catalog promotion of any candidate
- broad V4 speedup wording
- whole-app speedup wording
- true-zero-copy public wording
- Tier-3 callback support
- raw OptiX callback support
- embedding/C-ABI/non-Python host work
- app-specific native kernels
