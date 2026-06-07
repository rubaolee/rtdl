# Goal3719 RayJoin LSI Native Repeated Count Diagnostic Pod Validation

Date: 2026-06-07

## Purpose

Goal3717 showed that RTDL's current same-source RayJoin LSI path is correct but still slower than the original RayJoin executable on the bundled Brazil dataset. Goal3719 tests the most important immediate hypothesis: whether the remaining gap is caused mostly by Python/ctypes front-door overhead.

The diagnostic adds a native repeated-count ABI for the existing generic segment-pair prepared-left exact count route. It loops inside the native OptiX library over the same exact count operation and reports total, average, min, and max seconds. It does not change the counting algorithm, does not make the route a public default, and does not authorize any public speedup claim.

## Pod Evidence

Artifact:

`docs/reports/goal3718_segment_pair_prepared_left_repeated_count_a5000/summary.json`

Environment:

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX A5000, driver 580.126.09 |
| RTDL commit | `eb617478` |
| RayJoin commit | `02bf6220d6d20b04af77ee20364eced75cc029c9` |
| Dataset | RayJoin bundled Brazil county/soil text files |
| Left segments | 326,193 |
| Right segments | 251,011 |
| RayJoin repeat/warmup | 3 / 2 |
| RTDL Python repeat/warmup | 10 / 3 |
| RTDL native repeated count | 50 measured repeats after 5 native warmup repeats |

## Results

| Measure | Seconds | Interpretation |
| --- | ---: | --- |
| RayJoin LSI query | 0.000886679 | Original RayJoin executable timing |
| RTDL Python front door median | 0.001164439 | `prepared.count_prepared_left(...)` from Python |
| RTDL native repeated average | 0.001161695 | Native loop around same exact prepared-left route |
| Python/native ratio | 1.002x | Python/ctypes overhead is negligible for this path |
| Native repeated vs RayJoin | 0.763x | RTDL native route remains slower than RayJoin |

Correctness:

| Source | Count |
| --- | ---: |
| RayJoin LSI | 20,860 |
| RTDL Python front door | 20,860 |
| RTDL native repeated | 20,860 |

The counts match exactly. The native repeated path also checks count stability across every native repeat.

## Diagnosis

This result closes the "maybe Python overhead is the problem" branch for the current RayJoin LSI residual gap. The Python front door and native repeated loop differ by only about 0.2 percent. Removing Python/ctypes overhead does not bring the path close to RayJoin.

The remaining gap is therefore inside the native OptiX route or immediately adjacent native execution mechanics. The last Python-front-door native phase snapshot reports:

| Native phase field | Value |
| --- | ---: |
| `candidate_count_pass` | 0.000988025 s |
| `raw_candidate_count` | 20,972 |
| `emitted_count` | 20,860 |
| `candidate_download` | 0 |
| `candidate_write_pass` | 0 |
| `exact_refine` | 0 |
| `left_upload` | 0 |

This suggests the next useful work is a native-path inspection and optimization against RayJoin's own LSI implementation: launch shape, SBT layout, payload size, any-hit program structure, exact predicate placement, counter update strategy, OptiX pipeline options, and whether RTDL's generic route carries extra generic-contract costs that RayJoin avoids.

## Claim Boundary

This goal is diagnostic-only. It does not authorize:

- RTDL-beats-RayJoin claims.
- RayJoin paper reproduction claims.
- Public RT-core speedup claims.
- Release/default-route claims.
- True zero-copy claims.

## Next Engineering Target

Implement a native LSI route comparison packet that inspects RayJoin's LSI kernel mechanics against RTDL's generic segment-pair exact count route and proposes only app-agnostic changes. The likely useful targets are native launch/traversal/count mechanics, not Python adapters.
