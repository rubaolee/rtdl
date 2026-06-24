# Goal3531: Barnes-Hut P0 Recovery Investigation

Date: 2026-06-05

Status: Goal3527 Barnes-Hut P0 investigation complete for the focused A5000
slice. This is internal evidence only.

## Purpose

Goal3524 showed an unacceptable Barnes-Hut same-runner result:

- standard one-shot query, 8192 bodies: `0.401x`;
- weak rerun, 8192 bodies: `0.503x`.

Goal3527 made this the P0 weak row. The investigation question was whether the
current v2.8 fixed-radius node-coverage primitive is truly slower, or whether
the old same-runner row is dominated by cold one-shot measurement structure.

## Source Of Truth

Tracked pod artifacts:

- `docs/reports/goal3531_barnes_hut_p0_focus_a5000/summary.json`
- `docs/reports/goal3531_barnes_hut_p0_warm_probe_a5000/summary.json`

Pod metadata:

- SSH endpoint: `root@69.30.85.203 -p 22057`
- SSH key used by Codex: repo-local `id_ed25519_rtdl_codex`
- GPU: NVIDIA RTX A5000, driver `580.126.09`
- OptiX SDK path: `/root/vendor/optix-sdk`
- v2.3 evidence checkout: `2a28365d0246d51f3e3322b546f8a68c58632db4`
- v2.8 checkout: `d266b0370bcbcd4cbc24006ce9de2dfe783c1d2e`
- v2.3 OptiX library:
  `/root/rtdl_goal3524/v23_evidence/build/librtdl_optix.so`
- v2.8 OptiX library:
  `/root/rtdl_goal3524/v28_current/build/librtdl_optix.so`

## Static Finding

The Barnes-Hut node-coverage path still routes through the same generic
prepared scalar primitive:

```text
app.run_app("optix", optix_summary_mode="node_coverage_prepared")
  -> _run_prepared_node_coverage(...)
  -> rt.run_generic_prepared_fixed_radius_threshold_reached_count_2d(...)
  -> PreparedOptixFixedRadiusCountThreshold2D.count_threshold_reached(...)
  -> rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d
```

The visible Python wrapper body for the scalar threshold-count call is unchanged
between the v2.3 evidence commit and current v2.8. The native scalar-count
function also keeps the same basic launch structure: pack host query points,
upload query points, zero one device counter, launch the prepared fixed-radius
OptiX pipeline, synchronize, and download one scalar count.

This made a pure "wrong code path" explanation unlikely.

## Cold One-Shot Repeated Probe

The first focused pod packet repeated the old one-shot app process shape five
times for each checkout and scale.

| Body count | v2.3 median sec | v2.8 median sec | v2.8 / v2.3 speedup | Goal3527 close status |
| ---: | ---: | ---: | ---: | --- |
| 8192 | 0.011747295 | 0.025688133 | 0.457x | small-scale one-shot regression remains |
| 32768 | 0.045377322 | 0.047457722 | 0.956x | recovered for the larger one-shot scale |

This shows the Goal3524 8192 regression is reproducible under the old cold
one-shot process shape, but it also shows the regression does not scale with
the query size: at 32768 bodies the same contract is already within the 0.95x
Goal3527 recovery threshold.

## Warm Prepared-Query Probe

The second packet reused one prepared scene inside a single process, ran three
warmup queries, then measured twelve prepared queries. This isolates the
steady-state prepared query contract that the promoted v2.8 table should use.

| Body count | v2.3 warm median sec | v2.8 warm median sec | v2.8 / v2.3 speedup | Goal3527 close status |
| ---: | ---: | ---: | ---: | --- |
| 8192 | 0.009373441 | 0.009534039 | 0.983x | recovered |
| 32768 | 0.040364062 | 0.039779544 | 1.015x | recovered |

The warm prepared-query evidence crosses the `0.95x` Barnes-Hut close bar at
both scales. The observed problem is therefore not a steady-state v2.8 primitive
regression. It is a cold one-shot measurement problem in the old Goal2626 row.

## Engineering Decision

For Goal3527, Barnes-Hut should be reported in two lanes:

1. **Same-runner diagnostic lane:** keep Goal3524 visible. The old one-shot
   8192 row is still slower and must not be hidden.
2. **Promoted v2.8 lane:** use warm/repeated prepared-query timing for
   Barnes-Hut node coverage, with warmup count, repeat count, scale, and
   median/min/max recorded.

Do not use the old one-shot 8192 process metric as the v2.8 headline. It
measures cold process and first-query effects, not the reusable prepared RTDL
node-coverage primitive.

## What This Does Not Claim

Goal3531 does not authorize:

- public v2.8 release wording;
- public speedup wording;
- whole-app Barnes-Hut speedup wording;
- full RT-BarnesHut paper reproduction wording;
- broad RT-core speedup wording;
- true-zero-copy wording;
- app-specific native-engine behavior.

It only resolves the Goal3527 P0 question enough to proceed with the promoted
v2.8 performance table: Barnes-Hut node coverage must be measured as a warm
prepared-query contract, not as a cold one-shot process row.

