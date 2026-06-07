# Goal3698 Segment-Pair Precision-Guard Native Pod Validation

Date: 2026-06-07

## Purpose

Goal3697 widened the generic OptiX segment-pair conservative candidate slack from `1e-4` to `1e-3`, guided by Goal3693/Goal3696. Goal3698 validates that native policy change on the A5000 pod against the original RayJoin same-source LSI blocker.

This is a correctness repair validation, not a performance closeout.

## Pod Setup

Artifact directory:

- `docs/reports/goal3698_segment_pair_precision_guard_native_pod_a5000/`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- RTDL commit: `e8e700ae`
- Scoped RTDL source dirty: `false`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- RayJoin commit: `02bf622`

RayJoin checkout status includes local pod-only instrumentation:

- `M src/run_query.cu` for LSI pair dumping,
- `M src/util/markers.h` for the NVTX include repair,
- `?? release/` build directory.

## Validation Commands

The pod rebuilt the OptiX library from Git at `e8e700ae` and ran:

```text
python3 -m unittest \
  tests.goal3697_segment_pair_precision_guard_native_candidate_policy_test \
  tests.goal3696_segment_pair_precision_guard_contract_test \
  tests.goal3693_rayjoin_lsi_mismatch_localizer_test \
  tests.goal2169_optix_lsi_device_conservative_exact_filter_test
```

Result: `13` tests passed on the A5000 pod.

The same-source RayJoin probe then ran:

```text
python3 scripts/goal3691_rayjoin_original_same_source_probe.py \
  --rayjoin-root /root/RayJoin \
  --rayjoin-repeat 3 \
  --rayjoin-warmup 2 \
  --rtdl-repeat 5 \
  --rtdl-warmup 3 \
  --output docs/reports/goal3698_segment_pair_precision_guard_native_pod_a5000/summary.json
```

## Correctness Result

The Goal3691 LSI count mismatch is repaired:

| Metric | Before Goal3697 | After Goal3697 |
| --- | ---: | ---: |
| RayJoin checked LSI count | `20860` | `20860` |
| RTDL LSI count | `20859` | `20860` |
| RTDL minus RayJoin | `-1` | `0` |

The pair-set parity check is also clean after normalizing RTDL ids by subtracting one from both sides:

| Pair-set check | Value |
| --- | ---: |
| RayJoin pairs | `20860` |
| RTDL normalized pairs | `20860` |
| Missing from RTDL | `0` |
| Extra in RTDL | `0` |

This validates the Goal3693 diagnosis: the missing endpoint-near pair is recovered by the wider generic candidate guard, and exact refinement removes any false positives.

## Timing Result

Same-source query timing:

| Query | RayJoin query (s) | RTDL query (s) | RTDL / RayJoin speedup |
| --- | ---: | ---: | ---: |
| PIP | `0.000883341` | `0.000480420` | `1.839x` |
| LSI | `0.000876665` | `0.007232844` | `0.121x` |

The PIP row is unchanged in interpretation: RayJoin does not print a PIP count oracle, so it is promising but not count-comparable from this artifact.

The LSI row is now correct but still much slower than RayJoin. That is the next performance target.

## Interpretation

Goal3698 closes the immediate correctness blocker for same-source RayJoin LSI:

```text
RTDL now matches RayJoin's checked LSI count and exact pair set on the bundled Brazil sample.
```

It does not close the RayJoin performance target. RTDL is still using an exact prepared route that collects candidates and applies host-side exact refinement, while RayJoin's original implementation keeps a very compact RT queue path. The next useful engineering direction is a generic device-side or resident exact segment-pair count/refine path that preserves the Goal3698 pair parity without paying the current host-refine/materialization cost.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- public speedup claims,
- broad RT-core claims,
- true zero-copy claims.

It authorizes only this internal conclusion: the Goal3697 generic candidate guard repairs the same-source LSI pair-set correctness gap on the A5000 pod, while LSI performance remains an open RayJoin benchmark problem.

## Next Work

Recommended next goals:

1. add a generic device-side exact/refined segment-pair count path or resident candidate workspace,
2. avoid host row materialization for count-only LSI,
3. rerun RayJoin same-source LSI with both pair parity and query timing,
4. keep all naming and policies app-agnostic.

