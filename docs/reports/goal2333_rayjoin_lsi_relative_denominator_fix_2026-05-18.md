# Goal2333 RayJoin LSI Relative-Denominator Fix

Date: 2026-05-18

Status: `lsi-same-contract-mismatch-fixed-performance-still-behind`

## Purpose

Goal2332 found a serious RayJoin same-query blocker: on RayJoin-authored LSI
streams, RayJoin counted one more intersection than RTDL's prepared OptiX route.
The mismatch reproduced at both 4,096 and 65,536 generated query segments.

Goal2333 isolates that one-hit mismatch and fixes the generic host-side exact
segment-intersection refinement policy. This is a correctness fix, not a
performance win. RTDL now matches RayJoin's visible LSI intersection set on the
tested streams, but RTDL is still slower than RayJoin's specialized implementation.

## Root Cause

The broad-phase OptiX candidate pass already found the missing pair. The failure
was in host exact refinement:

```cpp
if (std::abs(denom) < 1.0e-7) {
    return false;
}
```

That absolute denominator threshold treated a real crossing as parallel because
the RayJoin query segment was short. The missing pair was:

| Field | Value |
| --- | ---: |
| query segment id | 2148 |
| base segment id | 226827 |
| RayJoin 4,096 count | 342 |
| RTDL pre-fix 4,096 count | 341 |
| RTDL raw candidate count | 342 |

The floating orientation magnitudes were small but sign-changing:

| Orientation | Value |
| --- | ---: |
| base against query p0 | `1.0024434043406439e-08` |
| base against query p1 | `-4.7411231355264614e-08` |
| query against base p0 | `-4.5413067951455264e-08` |
| query against base p1 | `1.2022597447223624e-08` |

So this was not an OptiX traversal miss. It was an over-aggressive absolute
epsilon in the generic exact-refine filter.

## Fix

The host-side exact segment-intersection code now uses a scale-aware denominator
test:

```cpp
scale = hypot(r) * hypot(s)
threshold = 64 * epsilon(double) * max(1, scale)
parallel if abs(denom) <= threshold
```

This keeps genuinely degenerate nearly-parallel pairs out while allowing short
but valid crossings to survive exact refinement.

Files changed:

| File | Change |
| --- | --- |
| `src/native/optix/rtdl_optix_core.cpp` | Replaced absolute `1e-7` denominator cutoff in host exact segment intersection with relative scale-aware test. |
| `src/native/embree/rtdl_embree_geometry.cpp` | Applied the same generic policy to Embree's CPU segment-intersection helper. |
| `src/native/oracle/rtdl_oracle_internal.h` | Added `<limits>` and the relative epsilon constant. |
| `src/native/oracle/rtdl_oracle_geometry.cpp` | Applied the same policy to the Oracle/native CPU reference helper. |
| `src/native/vulkan/rtdl_vulkan_core.cpp` | Applied the same policy to Vulkan's host-side exact segment-intersection helper. |

This keeps the engine app-agnostic: no RayJoin-specific symbol, dataset branch,
or app-shaped native continuation was added.

## Debug Patch

To isolate the mismatch, this goal adds a RayJoin debug patch:

`docs/research/rayjoin_lsi_result_export_debug_patch.diff`

The patch adds an environment-controlled result export hook:

```bash
RAYJOIN_EXPORT_LSI_XSECTS=/path/to/xsects.json query_exec ...
```

It writes `query_eid` and `base_eid` identity pairs from RayJoin's own LSI
intersection queue. This patch is diagnostic only; it is not part of RTDL's
runtime.

## Evidence

Pod:

| Item | Value |
| --- | --- |
| SSH host | `69.30.85.175` |
| SSH port | `22114` |
| Key actually used | `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod` |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| RTDL base commit on pod | `617b43aef389b91f8a9daa52e645c7a964fb9a1d` plus this local patch |
| RayJoin upstream commit | `02bf622 Update README.md` plus Goal2331 query-stream export patch and Goal2333 debug result-export patch |
| Dataset | `br_county_clean_25_odyssey_final.txt` |

Artifact directory:

`docs/reports/goal2333_rayjoin_lsi_mismatch_probe/`

## Before/After Identity Comparison

| Scale | RayJoin count | RTDL count before | Missing before | RTDL count after | Missing after | Extra after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 LSI queries | 342 | 341 | 1 | 342 | 0 | 0 |
| 65,536 LSI queries | 5,809 | 5,808 | 1 | 5,809 | 0 | 0 |

The 65,536 after-fix identity comparison reports:

```json
{
  "alignment": "one_based",
  "rayjoin_count": 5809,
  "rtdl_count": 5809,
  "missing_from_rtdl_count": 0,
  "extra_in_rtdl_count": 0,
  "same_contract_with_rayjoin_query_exec": true
}
```

## After-Fix Timing Snapshot

Regular RTDL replay after the fix:

| Workload | RayJoin query time | RTDL median query time | RTDL count | Correctness status |
| --- | ---: | ---: | ---: | --- |
| LSI | 0.460211 ms | 4.929 ms scalar / 4.948 ms rows | 5,809 | same identity set as RayJoin on exported stream |
| PIP | 0.389942 ms | 5.038 ms scalar / 5.061 ms rows | 5,783 | internally stable; RayJoin `query_exec` still does not print a visible PIP count |

The fix slightly increases LSI exact-refine cost for this stream because it no
longer drops the short-segment crossing. This is acceptable for correctness, but
it does not close the RayJoin performance gap.

## Validation

| Environment | Command | Result |
| --- | --- | --- |
| Windows repo | `py -3 -m unittest tests.goal2333_rayjoin_lsi_relative_denominator_fix_test tests.goal2332_rayjoin_same_contract_pod_evidence_test tests.goal2331_rayjoin_query_exec_export_patch_plan_test tests.goal2327_rayjoin_prepared_route_contract_test tests.goal2327_rayjoin_perf_tuning_packet_test` | 23 passed |
| RTX A5000 pod | `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12` | rebuilt `build/librtdl_optix.so` |
| RTX A5000 pod | `python3 -m unittest tests.goal2327_rayjoin_prepared_route_contract_test tests.goal2327_rayjoin_perf_tuning_packet_test tests.goal2331_rayjoin_query_exec_export_patch_plan_test` | 10 passed |
| Local Linux `192.168.1.20` | `make build-embree` | Embree 4.3.0 loaded |
| Local Linux `192.168.1.20` | `python3 -m unittest tests.goal2327_rayjoin_prepared_route_contract_test tests.goal2327_rayjoin_perf_tuning_packet_test` | 8 passed |

## Claim Boundary

This goal authorizes:

- a narrow correctness statement: RTDL prepared OptiX LSI now matches RayJoin's
  exported LSI identity set on the tested 4,096 and 65,536 streams.

This goal does not authorize:

- an RTDL-beats-RayJoin claim;
- a RayJoin paper reproduction claim;
- a broad RT-core speedup claim;
- a whole-app speedup claim;
- a v2.0 release decision.

## Design Lesson

The correctness problem was a generic primitive-contract issue, not a need for
RayJoin-specific engine customization. The right fix was to make the generic
segment-intersection refinement policy scale-aware.

The remaining performance problem is separate: RayJoin still wins because its
C++/CUDA/OptiX path fuses more of the workflow around its specialized layout.
RTDL's next performance leap remains a generic device-resident row-stream or
continuation primitive, not an app-shaped RayJoin native path.
