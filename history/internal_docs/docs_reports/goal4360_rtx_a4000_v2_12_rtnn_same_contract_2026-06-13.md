# Goal4360: RTNN Same-Contract OptiX vs Embree Row

Date: 2026-06-13

Status: internal same-contract backend comparison; not public RT-core speedup authorization.

## Result Table

| Backend | Query Median Sec | Prepare Sec | Rows | Bounded Neighbors | Nearest Checksum | Kth Checksum | Phase |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| optix | 0.103778298 | 2.488193561 | 65536 | 206256 | 2147450880 | 2148443891 | `prepared_uniform_cell_ranked_summary_rows` |
| embree | 0.122744617 | 0.073917684 | 65536 | 206256 | 2147450880 | 2148443891 | `embree_prepared_fixed_radius_ranked_summary_rows` |

Embree / OptiX query-median ratio: **1.18x**; faster backend: **optix**.

The raw-ranked-summary aggregate signature matches exactly across all integer fields and `sum_distance`.

## Interpretation

This closes RTNN as an output-contract mismatch for the optimized comparison packet: both sides run prepared 3-D fixed-radius bounded ranked-summary raw rows and produce identical row signatures. The observed OptiX advantage is modest because this current RTNN path uses the prepared fixed-radius ranked-summary implementation and reports prepared_uniform_cell_ranked_summary_rows rather than a proven RT-core traversal-specific path.

## Boundary

This row is fair for the selected RTNN output contract. It is not a full RTNN paper reproduction and it does not authorize broad RT-core wording, because the current OptiX neighbor-search phase is reported as `prepared_uniform_cell_ranked_summary_rows`.
