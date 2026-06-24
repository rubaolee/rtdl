# Goal 1517: Embree Prepared Summary Reuse Performance

## Verdict

`goal1517_embree_prepared_summary_reuse_perf_recorded`

- Valid: `True`
- Git commit: `f30e7d69afed2f0d23e87bc92c50cf899af7a956`
- Host: `lx1`
- Embree version: `(4, 3, 0)`
- Repeats: `5`
- Warmups: `1`

## Cases

| App | Copies | Points | Prepare sec | One-shot median sec | Prepared run median sec | Prepared/one-shot ratio | Summary rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| outlier | 512 | 4096 | 0.005995 | 0.019054 | 0.011712 | 1.627x | 4096 |
| dbscan | 512 | 4096 | 0.006004 | 0.019241 | 0.011915 | 1.615x | 4096 |
| outlier | 2048 | 16384 | 0.023529 | 0.083828 | 0.056446 | 1.485x | 16384 |
| dbscan | 2048 | 16384 | 0.023386 | 0.084066 | 0.055885 | 1.504x | 16384 |
| outlier | 8192 | 65536 | 0.092776 | 0.332714 | 0.217364 | 1.531x | 65536 |
| dbscan | 8192 | 65536 | 0.091874 | 0.327102 | 0.216661 | 1.510x | 65536 |

## Timing Scope

Measures repeated app summary phases with Python density/core conversion, but excludes full CLI JSON output and oracle work. Prepared mode reports run-only timing after one reusable Embree BVH prepare.

## Claim Boundary

Goal1517 records CPU Embree prepared-summary reuse timings for outlier and DBSCAN app summary phases. It does not authorize public speedup wording, broad RTX wording, whole-app claims, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, or release action.
