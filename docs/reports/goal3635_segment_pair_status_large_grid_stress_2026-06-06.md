# Goal3635 Segment-Pair Status Large-Grid Stress

Date: 2026-06-06

Verdict: `accept-with-boundary`

## Purpose

Goal3635 stress-tests the Goal3633 segment-pair dense-count/status residency
path on larger synthetic crossing grids while the RTX A5000 pod is available.
This is a robustness and diagnostic pass, not a public performance claim.

The tested primitive remains the same candidate generic
`segment_pair_left_id_dense_count` contract:

- strict v0 non-collinear endpoint-inclusive segment-pair predicate;
- dense left-id grouped count;
- OptiX prepared right-side segment scene;
- device-resident dense count plus overflow-status columns;
- source/candidate event count exposed as a device status pointer;
- validation downloads only for comparison against CuPy/analytic references.

## Artifact

Machine artifact:

- `docs/reports/goal3635_segment_pair_status_large_grid_a5000/summary.json`

Pod source state:

- source commit: `11b9721c`
- GPU: `NVIDIA RTX A5000, 8.6, 580.126.09`
- tracked source status: clean (`git_tracked_status_short == ""`)

## Results

All same-contract counts matched. The large grids exercise 4.19M and 16.78M
candidate pairs without materializing hit-pair rows.

| Case | Pair Count | OptiX Hits | Source Status | Overflow Status | Status Valid | Resident Columns | Full Residency |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| adversarial | 49 | 23 | 23 | 0 | yes | 2 | no |
| crossing_grid_2048 | 4,194,304 | 4,194,304 | 4,194,304 | 0 | yes | 2 | no |
| crossing_grid_4096 | 16,777,216 | 16,777,216 | 16,777,216 | 0 | yes | 2 | no |

## Diagnostic Timings

These timings are diagnostic only. The crossing-grid workload is an all-hit
synthetic case, so it is useful for stress and contract checking but not a broad
RayJoin or segment-pair speedup claim.

| Case | CuPy Dense Kernel Sec | CuPy Validation Reduce/Download Sec | OptiX Dense Wall Sec | OptiX Native Reduction Sec |
| --- | ---: | ---: | ---: | ---: |
| adversarial | 0.032251 | 0.024572 | 0.058782 | 0.000054 |
| crossing_grid_2048 | 0.000766 | 0.005992 | 0.005555 | 0.003159 |
| crossing_grid_4096 | 0.002922 | 0.000167 | 0.010844 | 0.006306 |

The diagnostic result is deliberately conservative: for this synthetic all-hit
dense arithmetic case, CuPy's dense kernel is faster than the OptiX traversal
route. The useful evidence here is that the strengthened status-column path
remains correct and bounded at larger scale; it does not authorize public RT-core speedup wording.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- RayJoin paper reproduction claims;
- making this route the native default.

The remaining residency gap is unchanged from Goal3633:

- `all_columns_device_resident`: `false`
- `fallback_required`: `true`
- `ambiguous_count` remains the explicit host-reference fallback

The next design question is whether to add a generic device-side segment-pair
classification/status post-pass or keep ambiguity as validation-only metadata
for the hot count route.
