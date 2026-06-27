# Phoenix V3 Fixed-Radius Symbol-Cache Focused Evidence

Date: 2026-06-22
Status: `focused_generic_runtime_fix_validated_not_release`

## Summary

This packet records the same-pod focused V2.14 vs current rerun after broadening
prepared fixed-radius count-threshold symbol/library caching in the generic
Embree and OptiX runtime surfaces.

The fix is generic runtime work, not benchmark-app-specific tuning:

- `src/rtdsl/embree_runtime.py`
  - `PreparedEmbreeFixedRadiusCountThreshold2D` and
    `PreparedEmbreeFixedRadiusCountThreshold3D` now cache optional native symbol
    lookups on the prepared object.
- `src/rtdsl/optix_runtime.py`
  - `PreparedOptixFixedRadiusCountThreshold3D` now caches library and optional
    native symbol lookups.
  - The 2-D OptiX device-search prepared path initializes and uses prepared
    symbol caching instead of resolving hot symbols repeatedly.
- `tests/v3_phoenix_prepared_fixed_radius_symbol_cache_test.py`
  - Adds focused regression tests for prepared fixed-radius symbol caching.

This does not authorize V3 release or broad V3-over-V2 performance wording. It
validates a useful generic runtime cleanup, with focused gains concentrated in
some OptiX fixed-radius Hausdorff rows. Barnes-Hut and RTDBSCAN remain near
parity in this packet.

## Evidence Boundary

Remote run:

```text
run_id: phoenix_v3_fixed_radius_symbol_cache_focused_20260622_144922
pod: root@213.173.108.14 -p 11592
remote_dir: /root/rtdl_v3_rebuild_20260620/phoenix_v3_fixed_radius_symbol_cache_focused_20260622_144922
hardware: NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
python: Python 3.12.3
case_repeat: 5
scope: goal2626 large and goal2636 stress rows for Hausdorff XHD, RTDBSCAN, and Barnes-Hut
```

Local copied artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_fixed_radius_symbol_cache_focused_20260622_144922/
```

Important contamination guard:

```text
This run does not include the later local src/rtdsl/partner_adapters.py
self-query refresh patch. Do not mix these evidence packets.
```

## Validation

Local validation before pod run:

```text
py_compile optix_runtime.py and embree_runtime.py: OK
targeted prepared fixed-radius tests: 4 OK
combined targeted runtime tests: 33 OK, 2 skipped
release/readiness/wording gates: 11 OK
```

Remote validation after sync:

```text
targeted runtime tests: 27 OK
```

Patched source hashes:

```text
src/rtdsl/optix_runtime.py 31f4fbf1ccaa9dae30bc0bbfac9d1087437db010eda0a31dccebaab24c5323df
src/rtdsl/embree_runtime.py 7b166ca9494f3a2f85803c8dc367eefcec5a04a595b90c8d786deb8007fb8b09
tests/v3_phoenix_prepared_fixed_radius_symbol_cache_test.py a049dd5e4e05bd28e41430c6e0e4049f08794dcf0345b3db2e86886dca6f07c6e
```

Copied summary hashes:

```text
current_goal2626_large_barnes_hut/summary.json 5995b2db778911a8d67e4246277f0f83dd1fb6e4a4a4aecf0682079589cdf6c0
current_goal2626_large_hausdorff_xhd/summary.json abd24c2f0044f0a8a6a7db1aa0b34ca24cedcfe7d414b5799415f27bb316084e
current_goal2626_large_rt_dbscan/summary.json 8a4d76e1cf2a611452674cccf819971c34ab31aa4001f15bfdc01839ebe98ac7
current_goal2636_stress_barnes_hut/summary.json feac889201d01ebd3435936f1014597d4e8d23ebad562806b6170b063aa4360b
current_goal2636_stress_hausdorff_xhd/summary.json 29edbd199f6d6564f6ae2bd219804baabf74aa966ce861f9f9a63b244913217e
v2_14_goal2626_large_barnes_hut/summary.json 163dedc38c698f10639e1d8a4f86dbdbfe1b499d83c5e5a39087c77b41874fbc
v2_14_goal2626_large_hausdorff_xhd/summary.json ab71b42e113b4b7f928ccd843dad14a7bd17e78231dd6332f63eeaed2070253c
v2_14_goal2626_large_rt_dbscan/summary.json ebd2ce11ea8458536faa7874d884e210f21360a5b922631a5108185254b52b81
v2_14_goal2636_stress_barnes_hut/summary.json 94fb73e982365c4c8c95e155f6ff8f0e9e5e6ac50bd905f6d7f4c5250ca93f54
v2_14_goal2636_stress_hausdorff_xhd/summary.json 552ba257821d06ad791124afd36391c3c7b2274fc2937093443534a1a7d3d910
```

## Focused Results

Analyzer method:

```text
same-case key: app_id + case_id + backend + comparison_group
primary metric: primary_metric_sec
missing paired keys: 0
comparison rows: 17
overall geomean current V3 speedup vs V2.14: 1.062x
rows faster by >5%: 4
rows within +/-5%: 12
rows slower by >5%: 1
```

Grouped geomeans:

| group | rows | geomean current V3 speedup vs V2.14 | min | max |
| --- | ---: | ---: | ---: | ---: |
| Barnes-Hut | 6 | 1.011x | 0.987x | 1.032x |
| Hausdorff XHD | 10 | 1.099x | 0.929x | 1.376x |
| RTDBSCAN | 1 | 1.009x | 1.009x | 1.009x |
| Embree backend | 8 | 1.001x | 0.970x | 1.032x |
| OptiX backend | 9 | 1.119x | 0.929x | 1.376x |

Same-case rows:

| suite | app | backend | case | V2.14 sec | current sec | speedup |
| --- | --- | --- | --- | ---: | ---: | ---: |
| goal2626 large | Barnes-Hut | Embree | `barnes_hut_embree_node_coverage` | 0.138453 | 0.134097 | 1.032x |
| goal2626 large | Barnes-Hut | OptiX | `barnes_hut_optix_node_coverage` | 0.043013 | 0.042521 | 1.012x |
| goal2626 large | Hausdorff XHD | Embree | `hausdorff_embree_threshold` | 0.572804 | 0.576582 | 0.993x |
| goal2626 large | Hausdorff XHD | OptiX | `hausdorff_optix_threshold` | 0.282240 | 0.230771 | 1.223x |
| goal2626 large | RTDBSCAN | Embree | `rt_dbscan_embree_fixed_radius_rows` | 114.390747 | 113.314535 | 1.009x |
| goal2636 stress | Barnes-Hut | Embree | `barnes_hut_embree_node_coverage_bodies_32768` | 0.132170 | 0.129666 | 1.019x |
| goal2636 stress | Barnes-Hut | Embree | `barnes_hut_embree_node_coverage_bodies_131072` | 0.550435 | 0.557454 | 0.987x |
| goal2636 stress | Barnes-Hut | OptiX | `barnes_hut_optix_node_coverage_bodies_32768` | 0.042469 | 0.042409 | 1.001x |
| goal2636 stress | Barnes-Hut | OptiX | `barnes_hut_optix_node_coverage_bodies_131072` | 0.299185 | 0.295246 | 1.013x |
| goal2636 stress | Hausdorff XHD | Embree | `hausdorff_embree_threshold_copies_16384` | 0.556667 | 0.574001 | 0.970x |
| goal2636 stress | Hausdorff XHD | Embree | `hausdorff_embree_threshold_copies_65536` | 2.529017 | 2.510546 | 1.007x |
| goal2636 stress | Hausdorff XHD | Embree | `hausdorff_embree_threshold_copies_262144` | 9.947931 | 10.040994 | 0.991x |
| goal2636 stress | Hausdorff XHD | OptiX | `hausdorff_optix_threshold_copies_16384` | 0.319519 | 0.232239 | 1.376x |
| goal2636 stress | Hausdorff XHD | OptiX | `hausdorff_optix_threshold_copies_65536` | 1.548082 | 1.570535 | 0.986x |
| goal2636 stress | Hausdorff XHD | OptiX | `hausdorff_optix_threshold_copies_262144` | 6.027096 | 6.486482 | 0.929x |
| goal2636 stress | Hausdorff XHD | OptiX | `hausdorff_optix_exact_grouped_seeded_pruned_points_32768` | 3.706647 | 2.715604 | 1.365x |
| goal2636 stress | Hausdorff XHD | OptiX | `hausdorff_optix_exact_grouped_seeded_pruned_points_131072` | 3.435937 | 2.696274 | 1.274x |

## Interpretation

This is a legitimate generic-runtime fix and should stay, but it is not a
Phoenix V3 release breakthrough.

What it proves:

- Prepared fixed-radius symbol/library lookup was real overhead in some hot
  paths.
- Caching those lookups on prepared runtime objects is correct generic engine
  cleanup.
- The focused packet produces a 1.062x geomean on 17 same-metric rows and a
  1.119x OptiX backend geomean.
- Hausdorff XHD OptiX rows benefit materially in several cases.

What it does not prove:

- It does not make V3 broadly faster than V2.x.
- It does not convert the earlier serious all-app 1.012x result into a major
  release result.
- It does not make execution graph, device residency, or fused continuation a
  productized V3 capability.
- It does not justify repeating the full all-app V2.14 vs V3 run yet.

Release decision remains:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## Next Engineering Action

Stop spending Phoenix V3 time on additional pure symbol-cache tweaks unless a
new serious row proves the same class of overhead is blocking a reusable
runtime primitive.

The next evidence-producing action should be the already-local generic
fixed-radius graph self-query refresh A/B:

- run current pod baseline without the local `partner_adapters.py` self-query
  patch;
- sync the patch;
- run the same focused RTDBSCAN / fixed-radius graph grouped-stream cases;
- classify the result as material generic runtime improvement, hygiene, or
  regression.

Only if that produces broad material improvement should another all-app V2.14
vs current Phoenix V3 run be considered.

## Goal-Level Decision Audit

1. Was I foolish?
   Yes, the earlier V3 process was foolish when it treated scoped row evidence
   and focused cleanups as if they could carry a major release claim.
2. If yes, what actions made the decision foolish?
   I let local wins and route-specific evidence create release momentum before
   all-app same-hardware V2.14 comparison proved broad material superiority.
3. Was there another possible path?
   Yes. The better path was to separate generic runtime capability promotion,
   focused regression repair, and release authorization from the beginning.
4. Can I now try a different path that truly solves the problem?
   Yes. The current path keeps this fix, records the limited evidence honestly,
   blocks release wording, and moves next to generic self-query/device-resident
   runtime work instead of app-specific tuning.
