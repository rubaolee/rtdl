# Goal4372 PIP 10-Second-Level RTDL OptiX vs Embree Comparison

## Hardware And Contract

- CPU: AMD EPYC 7702, 64 cores / 128 logical threads
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.08
- Embree: 4.3.0
- OptiX: optix-dev v8.0.0 headers; v8.1 headers failed on this driver with `Unsupported ABI version`
- Contract: RTDL Spatial RayJoin PIP prepared scalar count, count-only, no row materialization, exact row-count agreement

## Final Slice Comparison

| Dataset | Backend | Threads | Repeat | Row count | Hot total sec | Median/query ms | Prepare sec | Key native timing |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| br_county_start256_count512.cdb | OptiX / RTX 4000 Ada | n/a | 20000 | 1417 | 14.598 | 0.725 | 0.707 | candidate_write 0.240 ms; exact_refine 0.406 ms |
| br_county_start256_count512.cdb | Embree / CPU | 1 | 20000 | 1417 | 11.998 | 0.599 | 0.046 | native traversal median 0.583 ms |

Result: Embree is 1.22x faster by hot total and 1.21x faster by median/query on this PIP slice.

## Embree Thread Sweep On Slice

| Threads | Total sec | Mean/query ms | Median/query ms | P95 ms | P99 ms | Max ms |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 9.002 | 0.600 | 0.596 | 0.626 | 0.656 | 1.804 |
| 2 | 16.032 | 1.069 | 1.086 | 1.174 | 1.322 | 2.193 |
| 4 | 11.616 | 0.774 | 0.777 | 0.935 | 1.049 | 7.376 |
| 8 | 12.018 | 0.801 | 0.795 | 0.924 | 1.055 | 8.994 |
| 16 | 19.726 | 1.315 | 1.295 | 1.480 | 1.596 | 10.041 |
| 32 | 39.611 | 2.641 | 2.627 | 2.881 | 3.120 | 13.470 |
| 64 | 80.756 | 5.384 | 5.376 | 5.744 | 6.229 | 13.242 |
| 128 | 160.041 | 10.669 | 10.591 | 11.275 | 13.098 | 35.523 |

## Full br_county.cdb Supplement

| Dataset | Backend | Threads | Repeat | Row count | Hot total sec | Median/query ms | Prepare sec | Key native timing |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| br_county.cdb | OptiX / RTX 4000 Ada | n/a | 1000 | 47262 | 22.813 | 22.729 | 0.762 | candidate_write 0.686 ms; exact_refine 22.426 ms |
| br_county.cdb | Embree / CPU best total | 16 | 1000 | 47262 | 14.739 | 14.865 | 0.044 | native traversal median 14.181 ms |

Supplement result: Embree best-total is 1.55x faster by hot total. The OptiX full case is dominated by exact_refine (22.426 ms/query) rather than RT candidate traversal (0.686 ms/query).

## Interpretation

- The old PIP row saying Embree is faster is reproducible at human-scale timing, not a sub-second artifact.
- It is reasonable because this PIP path is not a pure RT traversal benchmark. Exact point-in-polygon refinement dominates or at least materially competes with traversal.
- On the slice, Embree single-thread wins because the per-query work is small and extra CPU threads add scheduling overhead.
- On the full CDB file, OptiX candidate traversal is still small compared with exact_refine, so RT cores cannot dominate the end-to-end PIP count.
- Public wording should be narrow: `For RTDL Spatial RayJoin PIP count, optimized Embree CPU is faster than the current OptiX/RT-core path because exact refinement dominates; this row is not evidence against RT-core acceleration for traversal-heavy RTDL workloads.`
