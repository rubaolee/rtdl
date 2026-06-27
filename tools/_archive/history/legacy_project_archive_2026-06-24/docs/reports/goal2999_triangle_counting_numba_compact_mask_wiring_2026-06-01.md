# Goal2999: Triangle Counting Numba Compact Mask Wiring

## Purpose

Goal2997 proved the generic `compact_mask_i64` continuation on an L4 pod. Goal2999 wires that primitive into a second benchmark-app surface: triangle counting.

This is deliberately not a replacement for the existing v2.5 triangle-counting fast path. The scalar triangle count remains primitive-first and uses the fused generic RTDL ray/triangle summary. The new v2.6 path exists for witness-row streams or post-summary tensor work where a user has candidate row ids and a boolean keep mask on a CUDA partner.

## What Changed

- Added `TRIANGLE_COUNTING_V2_6_NUMBA_COMPACT_MASK_VERSION`.
- Added `describe_triangle_counting_v2_6_numba_compact_mask_continuation()`.
- Added `v2_6_numba_compact_mask_plan_payload()` and CLI mode `--mode v2_6_numba_compact_mask_plan`.
- Added `run_triangle_counting_v2_6_numba_compact_mask_preview(inputs, block_size=...)`.
- Corrected the readiness next-action label from Goal2998 to Goal2999, because Goal2998 is the Gemini review for Goal2997.
- Updated the v2.6 roadmap to index Goal2999 as triangle-counting compact-mask app wiring.

## Contract

The app-level input columns are:

| Column | Type | Meaning |
| --- | --- | --- |
| `candidate_row_ids` | `int64` CUDA partner array | App-owned candidate/witness row identifiers. |
| `valid_triangle_mask` | `bool` CUDA partner array | App-owned validity mask over those row ids. |

The RTDL/Numba primitive sees only:

| Generic Operation | Input | Output |
| --- | --- | --- |
| `compact_mask_i64` | `values:int64`, `mask:bool` | `values:int64`, `original_indices:int64` |

Triangle candidate construction, duplicate filtering, and witness interpretation remain Python benchmark-app logic. The native engine is not given triangle-counting-specific continuation logic.

## Boundaries

- This is not a v2.6 release authorization.
- This is not a speedup claim.
- This is not a whole-app triangle-counting performance claim.
- This is not an RT-core speedup claim.
- This is not a true-zero-copy claim.
- This does not replace RT traversal.
- This does not change the primitive-first scalar triangle-counting recommendation.

## Why This Matters

The user-facing lesson is important: v2.6 can support a user-selected Numba partner path for non-scalar continuation work without forcing Triton, without using a torch carrier, and without putting app terms into the native engine. It turns Goal2997 from a standalone primitive proof into an app-surface wiring point.

## Validation

Local tests check that:

- the triangle-counting plan names only generic `compact_mask_i64`;
- host NumPy arrays fail closed before CUDA execution;
- the preview function uses the v2.6 neutral handoff and `run_numba_compact_mask_i64`;
- the v2.6 roadmap indexes Goal2999 without treating it as speedup evidence;
- the readiness action label no longer collides with Goal2998.

CUDA pod runtime evidence is still pending for this app wiring. Goal2997 already proved the underlying primitive on L4, but Goal2999 itself has not yet recorded an app-level pod artifact.
