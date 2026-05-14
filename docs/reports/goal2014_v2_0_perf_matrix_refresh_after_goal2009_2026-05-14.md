# Goal2014 v2.0 Perf Matrix Refresh After Goal2009

Date: 2026-05-14

Status: current-evidence-refresh-external-review-needed

## Scope

Goal2014 refreshes the v2.0 performance matrix narrative after Goals2000,
2003, 2006, and 2009. The earlier Goal1931/Goal1946 all-app tables remain
useful, but their road-hazard row predates the candidate-witness correction and
the prepared CuPy exact-filter cache.

This report does not regenerate every app artifact. It updates the current
interpretation of the all-app table so reviewers do not read stale Goal1889
road-hazard numbers as the best current evidence.

## What Changed Since Goal1931 / Goal1946

The most important change is the segment/polygon and road-hazard path:

1. Goal2000 corrected the native OptiX row contract to generic candidate
   witnesses and fixed the `float32` ray-column ABI.
2. Goal2003 moved exact segment/triangle filtering from host Python into a CuPy
   RawKernel for the unprepared hit-count column path.
3. Goal2006 extended exact CuPy filtering to prepared road-hazard reuse by
   retaining triangle columns in the Python partner wrapper.
4. Goal2009 cached the prepared triangle lookup, producing stronger prepared
   road-hazard evidence at counts 2048 and 4096.

The current best road-hazard row is therefore Goal2009, not the older Goal1889
row referenced by Goal1931.

## Updated Road-Hazard Evidence

### Count 2048

| Row | Median seconds | Ratio vs v1.8 prepared | Meaning |
| --- | ---: | ---: | --- |
| v1.8 one-shot native OptiX rows | 16.492227267 | 4741.70x slower | Cold-ish one-shot app row, not the fair prepared baseline. |
| v1.8 prepared native OptiX rows | 0.003478130 | 1.000x | Fair repeated-query baseline. |
| v2.0 unprepared CuPy priority columns | 0.003188476 | 0.917x | Positive, but still pays repeated setup. |
| v2.0 prepared CuPy cached exact-filter columns | 0.002519239 | 0.724x | Current best row; about `1.38x` faster than v1.8 prepared. |

Artifact:

- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_2048.json`

### Count 4096

| Row | Median seconds | Ratio vs v1.8 prepared | Meaning |
| --- | ---: | ---: | --- |
| v1.8 one-shot native OptiX rows | 104.259560453 | 10757.88x slower | One-shot app row explodes with candidate volume. |
| v1.8 prepared native OptiX rows | 0.009691451 | 1.000x | Fair repeated-query baseline. |
| v2.0 unprepared CuPy priority columns | 0.005996620 | 0.619x | About `1.62x` faster than v1.8 prepared. |
| v2.0 prepared CuPy cached exact-filter columns | 0.003932310 | 0.406x | Current best row; about `2.46x` faster than v1.8 prepared. |

Artifact:

- `docs/reports/goal2009_pod_smoke/road_hazard_prepared_cupy_cached_triangle_lookup_4096.json`

## Updated All-App Interpretation

Only one row should be changed immediately in the reader-facing all-app table:

| App row | Previous Goal1946 interpretation | Current Goal2014 interpretation |
| --- | --- | --- |
| `road_hazard_screening` | Positive compact-output row, small speedup at count 2048. | Stronger prepared CuPy exact-filter row. Native remains generic candidate-only; CuPy performs exact filtering, counting, and thresholding on device. Count 2048 is `1.38x` faster than v1.8 prepared; count 4096 is `2.46x` faster. |

Other rows keep their Goal1946 classification for now:

- fixed-radius family: still strongest broad v2 evidence;
- robot collision: still strong true device-handoff evidence;
- segment any-hit: still positive seconds-scale same-contract evidence;
- database, graph, polygon area, and polygon Jaccard: still bounded and need
  careful wording;
- exact partner-reference rows: useful semantic coverage, but not broad RT-core
  acceleration claims.

## Design Effect

Goal2009 changes the v2.0 story in a useful way:

```text
candidate native output + prepared partner companion state + device exact filter
+ partner reduction = exact app result without app-specific native code
```

That is exactly the v2.0 design target. The native engine stays app-agnostic,
and app-specific exact continuation is fast because it runs as partner GPU code
over device columns.

## Claim Boundary

Allowed:

- Road-hazard prepared CuPy has current pod evidence with exact parity and
  measured speedup versus v1.8 prepared native rows at counts 2048 and 4096.
- The speedup comes from partner-side exact filtering, unique-pair counting,
  thresholding, prepared scene reuse, and cached triangle lookup.
- Native OptiX remains a generic candidate-witness producer.

Not allowed:

- v2.0 final release authorization;
- broad RT-core speedup wording;
- claiming all apps are faster in a fair full-app sense;
- package-install claims;
- arbitrary PyTorch/CuPy acceleration claims;
- claiming Torch has the same device-side exact-filter path as CuPy.

## Next Refresh Needed

The next matrix update should produce a new machine-readable JSON successor to
`goal1931_current_all_app_v18_v2_perf_analysis_2026-05-13.json` that replaces
the road-hazard row with the Goal2009 evidence and records the source artifact
paths explicitly. This report is the narrative bridge; the JSON table remains a
separate follow-up.
