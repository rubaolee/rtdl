# Goal3359: Owner-Face Columnar Review Gap Closure

Date: 2026-06-04

Status: internal v2.8 gap-closure report. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3357 Claude review returned `accept-with-boundary` for Goals3349-3356 and identified four pre-lowering gaps. Goal3358 already closed the largest one by adding the seven-point real-artifact columnar fixture. Goal3359 closes or records the remaining items.

## Closure Map

| Claude finding | Closure |
| --- | --- |
| Missing end-to-end columnar fixture over the seven known mismatch points. | Goal3358 closed this with exact-row recovery and row/column parity over the Goal3328/3335 artifacts. |
| Silent topology-missing drop was undocumented. | Goal3359 adds `filter_policy.missing_topology = drop_candidate` to `owner_face_priority_pipeline_contract()`. |
| Optional topology presence columns were not tested. | Goal3359 tests `topology_has_left_faces` / `topology_has_right_faces` gating in the columnar filter path. |
| Conflicting owner-face selection rows should be covered. | Goal3359 adds an explicit fail-closed test; Goal3345 already had similar coverage. |

## Contract Update

The owner-face priority pipeline contract now exposes:

- `filter_policy.missing_owner = fail_closed_by_default`
- `filter_policy.missing_topology = drop_candidate`
- `filter_policy.topology_face_presence_columns = gate_left_and_right_face_ids_when_present`

The validator checks that the missing-owner and missing-topology policies remain explicit.

## Boundary

This is still not a native/device implementation. It is still a Python reference contract and test fixture.

Still blocked before promotion:

- native/device lowering,
- pod evidence for any lowered OptiX path,
- external review of the post-Goal3358/3359 closure state,
- release or public performance wording,
- RayJoin paper reproduction wording,
- RTDL-beats-RayJoin wording,
- broad RT-core speedup wording,
- true zero-copy wording.

The native engine must not infer ownership policy.

## Validation

Goal3359 tests verify:

- contract documents missing-topology drop behavior,
- columnar filter drops candidates whose topology row is absent,
- optional topology face-presence columns gate left/right face ids,
- conflicting owner-face selection rows fail closed,
- this report maps the Goal3357 review findings to closures.
