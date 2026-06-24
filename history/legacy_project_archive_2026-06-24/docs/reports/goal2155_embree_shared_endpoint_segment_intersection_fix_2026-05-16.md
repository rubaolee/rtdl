# Goal2155 Embree Shared-Endpoint Segment Intersection Fix

Date: 2026-05-16

Status: source fix implemented; clean pod evidence collected; external review pending.

## Purpose

Goal2153 found that the RayJoin public-CDB `lsi_county64_self_positive_control` diagnostic was not same-contract across backends: CPU and OptiX returned 4,766 segment-intersection rows, while Embree returned 3,809 rows.

Goal2155 fixes that as a generic Embree segment-pair intersection semantic gap. This is not RayJoin app customization.

## Root Cause

The Embree path casts each probe segment as a ray over right/build segments and collects intersecting build primitives from the Embree user-geometry callback.

That is fast for ordinary segment crossings, but the Goal2153 self-join showed a specific miss pattern:

- CPU minus Embree: 957 rows
- Embree extra rows: 0
- CPU minus OptiX: 0
- OptiX minus CPU: 0

Every sampled missing row was an adjacent same-chain pair sharing an endpoint. Example:

```text
missing ids 2096 2095
left  x0=-64.810699729 y0=-10.510532710 x1=-64.803564634 y1=-10.492460966
right x0=-64.823784736 y0=-10.509674500 x1=-64.810699729 y1=-10.510532710
```

The existing native code only fell back to a full exact scan when an Embree query returned zero rows. In a self-join, most probes had some non-endpoint hits, so shared-endpoint misses were not recovered.

## Fix

`src/native/embree/rtdl_embree_api.cpp` now builds a generic exact shared-endpoint index for the right/build segment set:

- `SegmentEndpointKey`
- `build_segment_endpoint_index`
- `append_shared_endpoint_segment_hits`

After the Embree callback and after the old zero-row full-scan fallback, the query path checks right/build segments that share either probe endpoint and runs the existing exact `segment_intersection` predicate before appending any missing rows.

This preserves the final stable ordering by sorting after the supplement.

## Pod Environment

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- Embree: 4.3.0
- Clean RTDL commit on pod: `9931585362e0e27ccf1a4e657afc7fd670209041`

Validation commands:

```bash
git fetch origin main
git reset --hard origin/main
PYTHONPATH=src:. RTDL_EMBREE_PREFIX=/usr make build-embree
PYTHONPATH=src:. RTDL_EMBREE_PREFIX=/usr python3 -m unittest tests.goal2155_embree_segment_endpoint_intersection_supplement_test
```

## Artifact

Collected artifact:

- `docs/reports/goal2155_rayjoin_external_cdb_warm_after_embree_endpoint_fix_pod_2026-05-16.json`

The artifact reruns the Goal2153 bounded public-CDB warm harness from the clean Goal2155 commit.

## Before And After

The key row is the self-join positive control:

| Backend | Goal2153 rows | Goal2153 parity | Goal2155 rows | Goal2155 parity |
| --- | ---: | --- | ---: | --- |
| CPU | 4,766 | pass | 4,766 | pass |
| Embree | 3,809 | fail | 4,766 | pass |
| OptiX | 4,766 | pass | 4,766 | pass |

Goal2155 resolves the same-contract mismatch for shared endpoint segment pairs.

## Goal2155 Warm Median Results

All rows below use one warmup and three measured repeats. Values are median app-level backend seconds, excluding cold-start OptiX module costs.

| Case | CPU sec | Embree sec | OptiX sec | Parity |
| --- | ---: | ---: | ---: | --- |
| `pip_county512` | 0.016789 | 0.004893 | 0.008679 | all pass |
| `lsi_county64_soil64` | 0.006031 | 0.012781 | 0.006676 | all pass, zero-hit slice |
| `lsi_county64_self_positive_control` | 0.013691 | 0.017975 | 0.006915 | all pass |
| `overlay_county128_soil128` | 0.154652 | 0.022441 | 0.025209 | all pass |

The endpoint supplement adds a small cost to Embree segment-pair queries, visible on the self-join row, but restores correctness. It does not materially change PIP or overlay, which use different paths.

## Claim Boundary

This goal authorizes:

- a generic Embree segment-pair shared-endpoint correctness fix
- clean pod evidence that the previous self-join mismatch is resolved
- continued use of the bounded public-CDB RayJoin harness as performance-development evidence

This goal does not authorize:

- full RayJoin paper reproduction
- paper-scale performance claims
- broad RT-core speedup claims
- whole-app RayJoin acceleration claims
- v2.0 release authorization

## Next Work

1. Add a reusable public-CDB RayJoin runner so the current one-off pod harness becomes repeatable source code.
2. Add a minimal endpoint-touch native parity fixture that can run on Linux when Embree is available.
3. Build CUDA/CuPy non-RT baselines for PIP and LSI on the same bounded public-CDB slices.
4. Find bounded public CDB pairs with nonzero cross-dataset LSI hits.

## Verdict

Goal2155 is accepted as a generic Embree correctness repair and a useful RayJoin v2 performance-development cleanup. External review is still needed before this evidence supports public wording.
