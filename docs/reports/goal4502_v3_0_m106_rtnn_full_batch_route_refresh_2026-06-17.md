# Goal4502 / V3 M106 RTNN Full-Batch Route Refresh

## Conclusion

M106 supersedes the M105 direct-graph-as-best RTDL wording for this KITTI-1M aggregate contract. The current fastest RTDL hot prepared aggregate is the full-batch non-graph prepared direct aggregate: it measures about 0.154s median query, 1.68x faster than the M105 direct graph row and 2.26x faster than the author synchronized total-search timer, while the author pure compute timer remains about 15x faster and the author cold process remains faster. The honest route split is aggregate-only full-batch direct, partner-continuation graph.

## Performance Matrix

| Row | Contract | Cold/process time | Hot/search time | Detail | Reading |
| --- | --- | ---: | ---: | --- | --- |
| Author RTNN C++/CUDA/OptiX | full K-id buffer copied to host | 2.050s process median | 0.347s total-search median | compute 0.010s; D2H 0.187s | specialized author RTNN route; fastest cold process and pure compute here |
| RTDL OptiX full-batch prepared direct aggregate | hot prepared float32 ranked-summary aggregate | 4.824s load+pack+prepare+query | 0.154s median query | one query batch of 1,000,000; no full neighbor-id materialization | current fastest RTDL aggregate-only route |
| RTDL OptiX direct graph M105 | hot prepared float32 ranked-summary aggregate | 4.710s load+pack+prepare+query | 0.257s median query | 65,536-query graph chunks; no full neighbor-id materialization | superseded for aggregate-only KITTI-1M |
| RTDL OptiX same-stream CuPy M105 | partner-continuation aggregate | 4.772s load+pack+prepare+query | 0.262s median query | same-stream device partial consumer | use when the app needs partner continuation |
| RTDL OptiX M104 generic | exact float64 ranked-summary aggregate | 12.827s load+pack+prepare+query | 7.803s median query | generic exact aggregate | superseded for this float32 hot aggregate contract |
| RTDL Embree M104 CPU | exact CPU ranked-summary aggregate | 123.307s load+pack+prepare+query | 120.928s median query | CPU aggregate; tie-sensitive kth checksum caveat | CPU fallback/proof row |

## Query Batch Sweep

| Query batch size | Batches | Repeat | Median query | Min | Max | Cold load+pack+prepare+query |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 16 | 3 | 0.257s | 0.256s | 0.266s | 5.551s |
| 131,072 | 8 | 3 | 0.195s | 0.194s | 0.201s | 4.736s |
| 262,144 | 4 | 3 | 0.171s | 0.169s | 0.174s | 4.770s |
| 524,288 | 2 | 3 | 0.162s | 0.161s | 0.162s | 4.885s |
| 1,000,000 | 1 | 3 | 0.155s | 0.154s | 0.155s | 4.732s |
| 1,000,000 | 1 | 10 | 0.154s | 0.152s | 0.157s | 4.824s |

## Ratios

- Full-batch prepared direct aggregate vs M105 direct graph: 1.68x faster.
- Full-batch prepared direct aggregate vs author synchronized total-search: 2.26x faster for RTDL aggregate query.
- Author synchronized compute phase vs full-batch RTDL aggregate: 14.95x faster for author compute.
- Full-batch prepared direct aggregate vs Goal4500 generic OptiX aggregate: 50.81x faster.
- Full-batch prepared direct aggregate vs Goal4500 Embree aggregate: 787.53x faster.
- Cold author process vs RTDL full-batch load+pack+prepare+query: author is 2.35x faster.

## Graph Cap Audit

- The current graph/device-partials path rejects prepared query handles above 65,536 queries.
- That cap does not block the aggregate-only best route: the non-graph prepared direct aggregate handles the full 1,000,000-query batch and is faster here.
- The graph/device-partials route remains useful when a same-stream partner continuation needs device partial rows instead of a final scalar aggregate.
- Next graph work should target large-query partner continuation or device partial reduction, not aggregate-only RTNN timing.

## Boundaries

- Same input: yes, all rows are read against the Goal4500 KITTI-1M CSV, radius 1.0, K=50, self-query contract.
- Same output surface with author RTNN: no. Author RTNN copies the full K-id result buffer; RTDL best returns ranked-summary aggregates.
- Paper reproduction: no. This is a bounded KITTI paper-family recipe, not the paper's exact frame recipe.
- Public speedup wording: still blocked. This is current-route evidence, not a public RT-core speedup claim.
