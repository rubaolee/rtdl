# Goal3691 RayJoin Original Same-Source Probe

Date: 2026-06-07

## Purpose

Goal3688 and Goal3690 compared RTDL candidate routes against dense all-CuPy same-contract baselines. That is useful for internal route tuning, but it does not answer the harder question: how does RTDL behave against the original RayJoin implementation on the same input files?

Goal3691 creates and runs a same-source probe against the RayJoin repository already present on the A5000 pod.

This is not a paper reproduction. It is a diagnostic comparison on RayJoin's bundled Brazil sample files.

## Implementation

New runner:

- `scripts/goal3691_rayjoin_original_same_source_probe.py`

New test:

- `tests/goal3691_rayjoin_original_same_source_probe_test.py`

The runner:

1. runs RayJoin `release/bin/query_exec` for PIP and LSI on the sample files,
2. runs RayJoin LSI once with `-check=true`,
3. runs RTDL cross-map PIP with county polygons and soil probe points using the Goal3686 native scalar-count executor,
4. runs RTDL exact prepared LSI on the same two files,
5. records timing, count, source, and claim-boundary metadata in one artifact.

## A5000 Evidence

Artifact:

`docs/reports/goal3691_rayjoin_original_same_source_probe_a5000/summary.json`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- RTDL source commit: `c8f9adf0`
- `goal3691_scoped_source_dirty=false`
- RayJoin source commit: `02bf622`
- RayJoin checkout status: `M src/util/markers.h`, `?? release/`

The RayJoin source modification is a build-environment include repair:

`#include <nvToolsExt.h>` -> `#include <nvtx3/nvToolsExt.h>`

Datasets:

- county: `/root/RayJoin/test/dataset/br_county_clean_25_odyssey_final.txt`
- soil: `/root/RayJoin/test/dataset/br_soil_ascii_odyssey_final.txt`

RayJoin loaded:

- county: `16545` chains, `342738` points, `326193` edges,
- soil: `7950` chains, `258961` points, `251011` edges.

## Results

Query-time comparison:

| Query | RayJoin query (s) | RTDL query (s) | RTDL / RayJoin speedup | Count status |
| --- | ---: | ---: | ---: | --- |
| PIP | `0.000879685` | `0.000471005` | `1.868x` | RayJoin PIP count not printed |
| LSI | `0.000897010` | `0.011885975` | `0.075x` | RTDL reports `20859`, RayJoin reports `20860` |

RayJoin LSI with `-check=true` also reported `20860` intersections.

RTDL PIP preparation timing:

| Phase | Seconds |
| --- | ---: |
| prepare static scene | `1.164843` |
| prepare point columns | `0.017657` |
| prepare native executor | `0.374689` |

RTDL LSI preparation timing:

| Phase | Seconds |
| --- | ---: |
| static segment pack | `0.006384` |
| prepare static scene | `0.536524` |
| query pack | `0.010428` |

## Interpretation

This is the most useful RayJoin evidence from this round because it separates two stories:

1. **Cross-map PIP is promising.** RTDL's generic native closed-shape scalar-count executor is faster than RayJoin's PIP query time on the same sample files. The count cannot yet be compared because RayJoin's `query_exec` timing output does not print the PIP hit count.
2. **LSI is still a blocker.** RTDL's current exact prepared LSI route is much slower than RayJoin's LSI query and disagrees by one intersection on this sample. The next RayJoin-facing work should focus on this LSI contract/performance gap, not more PIP scalar-count micro-tuning.

The LSI result likely reflects a difference between RTDL's host double exact-refinement policy and RayJoin's integer-scaled/high-precision policy. That must be diagnosed before any same-source RayJoin performance claim can be made.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- public speedup claims,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- broad RT-core speedup claims,
- true zero-copy claims.

Goal3691 only authorizes this internal engineering conclusion: on RayJoin's bundled Brazil sample, RTDL has a promising same-source PIP query-time result but has a clear LSI correctness/performance blocker.

## Next Work

Recommended next steps:

1. build a small LSI mismatch localizer for the one missing intersection,
2. compare RTDL's segment-pair predicate against RayJoin's scaled predicate on the mismatching pair,
3. decide whether RTDL needs a generic integer-scaled segment-intersection predicate mode,
4. rerun same-source PIP with a RayJoin count oracle if a count-printing or output path can be enabled,
5. keep original-RayJoin comparisons separate from dense all-CuPy same-contract baselines.
