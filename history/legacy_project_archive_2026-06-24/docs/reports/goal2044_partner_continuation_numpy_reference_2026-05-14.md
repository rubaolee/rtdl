# Goal2044 Partner Continuation NumPy Reference

Date: 2026-05-14

Status: `accept-with-boundary`

## Purpose

Goal2043 defined the v2.0 design gap: RTDL needs generic partner continuation contracts rather than app-specific native continuations.

Goal2044 implements the first concrete slice:

- a backend-neutral candidate-row schema;
- NumPy reference segmented reductions;
- NumPy reference group top-k;
- NumPy reference witness-carrying `group_argmin_then_global_argmax`;
- an exact Hausdorff-with-witness path using those generic primitives.

This is intentionally CPU-reference first. It gives local Linux a clean development platform for rich v2.0 semantics before pod-only CuPy/OptiX evidence is required.

## Files

- `src/rtdsl/partner_continuations.py`
- `examples/rtdl_hausdorff_distance_app.py`
- `tests/goal2044_partner_continuation_numpy_reference_test.py`

## New Generic Contracts

| Contract | Function |
| --- | --- |
| candidate row schema | `PartnerCandidateRows` |
| segmented count | `numpy_segmented_count` |
| segmented sum | `numpy_segmented_sum` |
| segmented min/max | `numpy_segmented_minmax` |
| group top-k | `numpy_group_topk` |
| witness-carrying reduction | `numpy_group_argmin_then_global_argmax_with_witness` |
| point row adapter | `point_rows_to_numpy_columns` |
| exact directed Hausdorff | `directed_hausdorff_2d_numpy_columns` |

These names are deliberately generic. They do not mention facility, ANN, Hausdorff, road, robot, or overlay in the primitive layer.

## Hausdorff Conversion

`examples/rtdl_hausdorff_distance_app.py` now has a `partner_numpy_exact` backend.

The path:

1. converts Python point rows into generic NumPy point columns;
2. builds generic source-target distance candidates;
3. computes per-source nearest target by `group_topk(k=1)`;
4. computes the directed Hausdorff witness by taking global max over those per-source minima;
5. compares the two directed passes for the undirected Hausdorff result.

This addresses one of the Goal2043 rich requirements: exact Hausdorff distance with witness extraction, at least as a clean NumPy reference contract.

## What This Solves

- The exact Hausdorff-with-witness semantics are no longer only an app-local Python loop.
- The reduction shape is reusable by other apps that need "per-group best, then global worst" logic.
- Local Linux can validate the rich contract without CUDA, CuPy, Torch, or a pod.
- The native engine remains app-agnostic.

## What This Does Not Yet Solve

- It does not make exact Hausdorff fast at large scale.
- It does not provide a CuPy implementation of the witness-carrying continuation.
- It does not provide an OptiX zero-copy candidate-row handoff for this exact rich contract.
- It does not solve exact K=3 facility ranking, ANN recall optimization, or general polygon overlay.
- It does not authorize v2.0 release.

## Next Step

The next implementation step should port the same generic contracts to CuPy:

- `cupy_group_topk`;
- `cupy_group_argmin_then_global_argmax_with_witness`;
- same-contract Hausdorff exact witness over device rows.

After that, pod evidence can decide whether exact rich Hausdorff should be an accepted v2.0 performance row or remain a correctness/reference row while threshold Hausdorff carries the fast decision-contract claim.

## Verdict

`accept-with-boundary`

Goal2044 is a clean v2.0 architecture step, not a performance closure.
