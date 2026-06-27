# Goal4501 / V3 M105 RTNN Author Same-Input Comparison

## Conclusion

RTDL V3 current best makes the KITTI-1M RTNN aggregate path genuinely subsecond after data and graph preparation, and it is about 30x faster than the older generic Goal4500 OptiX aggregate. The author C++/CUDA/OptiX implementation still maps the same search workload to RT cores much more efficiently at the pure compute phase, and it is faster on cold whole-process time. The comparison is useful, but it must be reported by contract: author full K-id materialization versus RTDL hot prepared ranked-summary aggregate are not the same output surface.

## Performance Matrix

| Row | Contract | Cold/process time | Hot/search time | Compute/materialization detail | Reading |
| --- | --- | ---: | ---: | --- | --- |
| Author RTNN C++/CUDA/OptiX | full K-id buffer copied to host | 2.050s process median | 0.347s total-search median | compute 0.010s; D2H 0.187s | specialized RTNN route; fastest cold full process here |
| RTDL OptiX direct graph | hot prepared float32 ranked-summary aggregate | 4.710s load+pack+prepare+query | 0.257s median query | device aggregate; no full neighbor-id materialization | current best RTDL aggregate route |
| RTDL OptiX same-stream CuPy | partner-continuation aggregate | 4.772s load+pack+prepare+query | 0.262s median query | same-stream CuPy consumer; no host scalar/partial read before consumer | use when partner continuation is required |
| RTDL OptiX M104 generic | exact float64 ranked-summary aggregate | 12.827s load+pack+prepare+query | 7.803s median query | generic aggregate without prepared-query graph replay | superseded by M105 graph path for this contract |
| RTDL Embree M104 CPU | exact CPU ranked-summary aggregate | 123.307s load+pack+prepare+query | 120.928s median query | CPU aggregate; tie-sensitive kth checksum caveat | CPU fallback/proof row, not the RT target |

## Ratios

- RTDL direct graph hot aggregate vs author synchronized total-search: 1.35x faster for RTDL aggregate query.
- Author synchronized compute phase vs RTDL direct graph hot aggregate: 25.06x faster for author compute.
- RTDL direct graph vs Goal4500 generic OptiX aggregate: 30.31x faster.
- RTDL direct graph vs Goal4500 Embree aggregate: 469.76x faster.
- Cold author process vs RTDL load+pack+prepare+query: author is 2.30x faster.

## Boundaries

- Same input: yes, the author RTNN and RTDL rows use the same Goal4500 KITTI-1M CSV, radius 1.0, K=50, self-query contract.
- Same output surface: no. Author RTNN copies the full K-id result buffer; RTDL best rows return ranked-summary aggregates.
- Paper reproduction: no. The KITTI row is a bounded paper-family recipe, not the paper's exact frame recipe.
- Author patch: external compatibility only, for CUDA 12/Ada architecture consistency; it does not change the neighbor-search algorithm.
