# Goal5104 RT-DBSCAN Author Warm-Loop Comparison

## Status

`completed_author_warm_loop_comparison`

## Purpose

Goal5100 showed RTDL warm in-process medians of about 4-6 ms, but the author side did not have an equivalent warm-process loop. Goal5104 adds a patched AuthorOfficial warm-loop comparator so the representative synthetic fixtures can be measured with both sides repeating in a long-lived process.

## Implementation

New AuthorOfficial incremental patch:

```text
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5104_authorofficial_warm_repeat_loop.patch
```

It applies after the Goal5092 AuthorOfficial JSON-output patch and adds:

- `RTDL_AUTHOR_REPEAT` environment variable;
- repeat loop around the author's call-1/core and call-2/cluster launches;
- per-repeat reset of the `DisjointSet` frame buffer;
- per-repeat JSON fields `repeat_index` and `repeat_count`;
- `cudaDeviceSynchronize()` after call-2 before timing/payload extraction.

New setup script:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/setup_authorofficial_warm_loop.sh
```

New matrix runner:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_warm_loop_matrix.py
```

The runner records:

- author same-process warm-loop payloads;
- author process wall for one repeated invocation;
- author inner-loop time = `core_points_time_sec + cluster_formation_time_sec`;
- author reported total time = build + core + cluster, retaining the author's prior total convention;
- RTDL repeated in one Python process;
- partition/core/signature equality for every repeat.

## POD Evidence

Summary:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_warm_loop_matrix_pod_summary.json
```

Author raw outputs:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_warm_loop_outputs/
```

Overall:

```text
all_cases_matched=true
repeat=5
regime=author_and_rtdl_warm_repeat_same_process_per_side
paper_reproduction_claim_authorized=false
performance_claim_authorized=false
whole_program_speedup_claim_authorized=false
```

## Results

Steady median excludes the first repeat on each side.

| Case | Author inner-loop steady median | Author total steady median | RTDL steady median | RTDL / author inner-loop |
|---|---:|---:|---:|---:|
| `representative_medium_two_clusters3d` | 0.040645s | 0.043406s | 0.003942s | 0.097x |
| `representative_border_shell3d` | 0.018776s | 0.021720s | 0.003864s | 0.206x |
| `representative_three_components_noise3d` | 0.015787s | 0.018570s | 0.003736s | 0.237x |

## Interpretation

The prior concern was valid: author needed a warm-loop counterpart before RTDL's 4-6 ms warm medians could be read fairly. Goal5104 supplies that counterpart for the representative synthetic fixtures.

On these bounded synthetic fixtures, the author warm loop remains at about 15.8-40.6 ms inner-loop steady median, while RTDL stays at about 3.7-3.9 ms steady median. Thus the warm-process RTDL advantage remains under this specific representative same-input diagnostic.

## Boundary

This still does not authorize:

- full RT-DBSCAN paper reproduction,
- exact paper dataset performance,
- public whole-program speedup,
- author-performance parity on paper workloads,
- exact author output format parity,
- a DBSCAN-native RTDL core primitive.

The result is a bounded representative warm-loop diagnostic only.
