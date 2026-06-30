# Goal3725 RayJoin LSI Grouped-Range Policy Sweep

Date: 2026-06-07

## Purpose

Goal3719 showed that Python/ctypes overhead is not the material cause of RTDL's same-source RayJoin LSI gap. Goal3723 showed that simply moving the exact segment predicate into the OptiX intersection program, without changing the primitive representation, did not help.

Goal3724 then introduced a diagnostic generic right-primitive range representation: one BVH primitive can carry a contiguous range of generic right-side segments, and the custom intersection program evaluates the exact predicate against that range. Goal3725 measures the policy space for that range representation on the RayJoin bundled Brazil LSI workload.

The key result is that the winning policy is not aggressive grouping. The winning policy is an identity range (`max_size=1`): keep one segment per traversable primitive, but run the exact predicate inside the custom intersection program and avoid the any-hit callback path. Larger ranges produce more false exact tests inside the intersection program and quickly become slower.

## Evidence

Artifacts:

- `docs/reports/goal3724_rayjoin_lsi_grouped_range_route_sweep_a5000/summary.json`
- `docs/reports/goal3724_rayjoin_lsi_grouped_range_route_confirm_a5000/summary.json`
- `docs/reports/goal3724_rayjoin_lsi_grouped_range_route_confirm_a5000/max1_area1.5.json`
- `docs/reports/goal3725_rayjoin_lsi_grouped_range_default_a5000/summary.json`

Environment:

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000, driver 580.126.09 |
| RTDL commit | `19b03599` for measurement; default policy updated afterward in this goal |
| RayJoin commit | `02bf6220d6d20b04af77ee20364eced75cc029c9` |
| Dataset | RayJoin bundled Brazil county/soil text files |
| Query orientation | soil edges as left/query rays; county edges as right/base segments |
| Query segments | 251,011 |
| Base segments | 326,193 |
| Correct count | 20,860 |

## Best Confirmation Row

The confirmation run used 3 warmups and 15 measured repeats for RTDL, and the RayJoin runner's configured warmup/repeat path for the same bundled LSI query.

| Route | Median/query seconds | Count | Relative |
| --- | ---: | ---: | ---: |
| RayJoin LSI query | 0.000905673 | 20,860 | 1.000x RayJoin |
| RTDL existing any-hit exact count | 0.001490480 | 20,860 | 0.608x vs RayJoin |
| RTDL grouped-range direct exact count, `max_size=1` | 0.000281732 | 20,860 | 3.215x vs RayJoin |
| RTDL grouped-range direct exact count, `max_size=1` | 0.000281732 | 20,860 | 5.290x vs existing RTDL any-hit |

This is a same-contract count result for one RayJoin LSI dataset and one GPU. It is strong engineering evidence for the primitive route, but it is not a public RayJoin reproduction claim.

## Default-Policy Validation

After changing the diagnostic route's native and runner defaults, a clean pod run reset to `origin/main` at commit `aa1f6cfb`, rebuilt `librtdl_optix.so`, and ran the same probe with no `--group-max-size` or `--group-area-enlarge` override. The runner selected `max_size=1, area_enlarge=1.5` by default and reproduced the result:

| Route | Median/query seconds | Count | Relative |
| --- | ---: | ---: | ---: |
| RayJoin LSI query | 0.000897725 | 20,860 | 1.000x RayJoin |
| RTDL existing any-hit exact count | 0.001428726 | 20,860 | 0.628x vs RayJoin |
| RTDL grouped-range direct exact count, default policy | 0.000272803 | 20,860 | 3.291x vs RayJoin |
| RTDL grouped-range direct exact count, default policy | 0.000272803 | 20,860 | 5.237x vs existing RTDL any-hit |

## Policy Sweep

The first sweep skipped RayJoin in intermediate rows and compared grouped-range policy against the existing RTDL any-hit route. The best row in that sweep was `max_size=4, area_enlarge=1.5`, at 0.000428 s. The follow-up confirmation added smaller policies and RayJoin timing; `max_size=1` was best.

| Policy | Groups | Compression | Grouped seconds | Speedup vs existing any-hit | Speedup vs RayJoin |
| --- | ---: | ---: | ---: | ---: | ---: |
| `max=1, area=1.5` | 326,193 | 0.000 | 0.000281732 | 5.290x | 3.215x |
| `max=2, area=1.5` | 281,837 | 0.136 | 0.000366604 | 3.877x | 2.406x |
| `max=3, area=1.5` | 270,766 | 0.170 | 0.000390192 | 3.818x | 2.250x |
| `max=4, area=1.5` | 265,430 | 0.186 | 0.000422384 | 3.517x | 2.096x |
| `max=4, area=2.0` | 187,139 | 0.426 | 0.000552919 | 2.704x | 1.593x |

The wider sweep also showed the failure mode:

| Policy | Groups | Grouped seconds | Speedup vs existing any-hit |
| --- | ---: | ---: | ---: |
| `max=16, area=2.0` | 118,045 | 0.001397888 | 1.034x |
| `max=32, area=2.0` | 91,068 | 0.002932702 | 0.533x |
| `max=64, area=2.0` | 71,846 | 0.006519067 | 0.221x |

Too much grouping lowers BVH primitive count but enlarges primitive boxes and increases the exact inner loop work inside the intersection program. For this LSI count contract, that tradeoff is bad.

## Engineering Decision

This goal changes the grouped-range diagnostic route's default policy from `max_size=64, area_enlarge=5.0` to `max_size=1, area_enlarge=1.5`.

That is intentionally conservative:

- It keeps the native engine app-agnostic: the ABI still talks about generic segment-pair intersection, prepared segment sets, and right-side primitive ranges.
- It avoids RayJoin-specific map, polygon, county, soil, or LSI vocabulary in native code.
- It keeps environment overrides for future datasets where a non-identity range might win.
- It does not promote this diagnostic route as a public default route yet; it makes the diagnostic route's own default match the measured safe policy.

## What We Learned

The decisive improvement is not host-side orchestration, and it is not bulk grouping by itself.

The useful primitive is:

> a generic exact segment-pair count route where the BVH candidate and exact predicate are resolved inside the custom intersection program, with one generic segment record per primitive unless a measured policy proves grouping is safe.

This is the first RayJoin LSI slice where RTDL's generic path is faster than the same-source RayJoin executable on the measured query contract. It should guide the next RayJoin work, especially parity/count contracts where the app only needs a grouped count or Boolean result rather than full witness rows.

## Claim Boundary

This goal does not authorize:

- RTDL-beats-RayJoin public claims.
- RayJoin paper reproduction claims.
- Broad RT-core speedup claims.
- v2.8/v2.9/v3.0 release claims.
- True zero-copy claims.
- Whole-app RayJoin acceleration claims.

The result is a diagnostic single-contract A5000 measurement with matching counts. It should be sent for external review before it is used in any release-facing performance table.
