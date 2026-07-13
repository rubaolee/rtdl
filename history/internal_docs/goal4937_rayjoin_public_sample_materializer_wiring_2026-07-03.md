# Goal4937 RayJoin Public Sample Materializer Wiring

Date: 2026-07-03

## Verdict

`byte_equal_but_not_faster_stop`

Goal4937 wired the generic grouped-output materializer from Goal4936 into the RayJoin Section 5.7 public sample app path as an app-layer experiment. The route preserved byte-for-byte correctness, but it did not beat the existing writer. The experimental code was therefore not retained in the source tree.

## Purpose

Goal4936 proved that the generic grouped-output materializer is much faster than a Python reference loop on a synthetic grouped-output workload. Goal4937 tested whether that primitive gives an immediate RayJoin Section 5.7 writer speedup on the bounded public sample.

The test intentionally kept RayJoin semantics out of RTDL core:

- RTDL generic primitive: grouped output descriptors/items.
- RayJoin app layer: output-chain semantics and author-compatible text formatting.
- No public release-surface change.

## Experiment

The RayJoin `section57_overlay_numba.py` writer path was temporarily changed to:

1. Keep output-chain descriptors as numeric arrays.
2. Keep output points as numeric item arrays.
3. Build a `GroupedOutputRowBufferSchema`.
4. Call `prepare_grouped_output_row_buffer`.
5. Call `materialize_grouped_output_row_buffer`.
6. Format the author-compatible text in the RayJoin app layer.

The first POD run used full descriptor validation. The second run disabled redundant group descriptor validation in the app adapter to test the obvious bounded fix.

## POD

- Host: `157.157.221.29:24344`
- GPU: NVIDIA RTX 4000 Ada Generation
- Dataset: RayJoin public sample, County x Soil
- Correctness gate: output byte equality against the public answer file
- Artifacts:
  - `history/internal_docs/goal4937_pod_artifacts/first_run/`
  - `history/internal_docs/goal4937_pod_artifacts/rerun1/`

## Results

| Run | Route | Byte Equal | Total Elapsed | Writer Time |
|---|---:|---:|---:|---:|
| first_run | existing plain writer | true | 6.764782s | 2.049810s |
| first_run | generic materializer wiring | true | 8.294726s | 4.688221s |
| rerun1 | existing plain writer | true | 6.121220s | 2.537364s |
| rerun1 | generic materializer wiring, no descriptor validation | true | 6.653871s | 3.067069s |

Rerun1 materializer writer phase breakdown:

| Phase | Seconds |
|---|---:|
| `chain_loop_map0_sec` | 0.930846 |
| `chain_loop_map1_sec` | 0.791196 |
| `generic_output_assembly_sec` | 1.037157 |
| `bulk_writelines_sec` | 0.064876 |
| `skip_plan_sec` | 0.064433 |
| `group_xsects_map0_sec` | 0.006953 |
| `group_xsects_map1_sec` | 0.080330 |

The materializer processed:

- `group_count`: 64,459
- `item_rows`: 673,371
- `descriptor_column_count`: 5
- `item_payload_column_count`: 2

## Interpretation

The route is correct but not faster.

The initial failure was partly descriptor validation overhead: `generic_output_assembly_sec` improved from 2.633837s to 1.037157s after disabling redundant validation. But the full writer still missed the gate because the materializer was inserted after the app had already paid the same chain-loop structure cost:

- existing route already has chain loop cost,
- materializer route still has chain loop cost,
- then materializer adds another generic assembly pass,
- final author-compatible text formatting still remains in the app layer.

So this wiring did not replace the expensive RayJoin output structure assembly; it added a generic materialization layer after it.

## Gate

The performance gate was not met.

- Minimum useful gate: materializer writer below the existing plain writer on the same run.
- Observed: 3.067069s materializer writer vs 2.537364s plain writer in rerun1.

No RayJoin speedup claim is authorized.

## Source State

The experimental `section57_overlay_numba.py` edits were reverted. The source tree should not retain a slower app route.

Retained assets are only:

- this completion report,
- the POD JSON artifacts,
- review packet files.

## What This Teaches

Goal4937 falsifies the shallow Layer 3 integration:

> A generic materializer attached after the RayJoin app has already built chain structures is not enough.

The next Layer 3 design must move the generic boundary earlier:

- input should be primitive row buffers or minimally structured row arrays,
- generic code should own grouping/descriptor/item materialization directly,
- RayJoin should only supply a thin author-format adapter after generic structure generation.

If the next design cannot remove the app chain-loop phase, it will repeat this failure.

## Exit Label

`byte_equal_but_not_faster_stop`
