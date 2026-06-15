# RayJoin County x Zipcode Current Comparison - 2026-06-14

## Scope

This packet uses the currently available same-source regenerated CDB pair, not the unavailable paper-preprocessed Dryad CDB:

- County map0: 8,662,896 chains/segments, 17,325,792 points.
- Zipcode map1: 9,503 chains, 5,279,181 segments, 5,288,684 points.
- Programs covered: LSI, PIP, and polygon overlay.
- Hardware comparison: RTDL OptiX on NVIDIA RT-capable GPU versus RTDL Embree on CPU.
- Author baseline: `rubaolee/RayJoin` C++/CUDA/OptiX RT mode, same CDB inputs and flags.

## Main Table

| Program | Implementation | Correctness / count | Measurement window | Hot median | Native traversal | End-to-end / total | Speedup vs RTDL Embree | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| LSI | RayJoin author RT | 180,506 intersections | warmup 5, repeat 2000 | 4.386 ms/query | not separated | 17.111 s process elapsed | n/a | Author C++/OptiX baseline. |
| LSI | RTDL OptiX | 180,506, exact vs author | warmup 5, repeat 6000 | 1.694 ms/query | 1.662 ms | 10.178 s hot loop | 183.4x hot, 186.8x native | Strong RT-core acceleration; best RTDL result. |
| LSI | RTDL Embree | 180,506, exact vs author | warmup 5, repeat 34 | 310.546 ms/query | 310.461 ms | 11.585 s hot loop | 1.0x | CPU BVH traversal is the bottleneck. |
| PIP | RayJoin author RT | Count not emitted by author query path | warmup 5, repeat 1500 | 7.200 ms/query | not separated | 16.257 s process elapsed | n/a | Very fast author closest-edge-id GPU path, but no comparable positive-face count in this mode. |
| PIP | RTDL OptiX host-points count | 3,823,783, exact vs RTDL Embree under shared-scale CDB contract | warmup 5, repeat 60 | 273.922 ms/query | 118.870 ms | 16.453 s hot loop | 1.12x hot, 2.57x native | Includes Python/native call and per-repeat upload of 5,288,684 query points. |
| PIP | RTDL OptiX device-resident count | 3,823,783, exact vs RTDL Embree under shared-scale CDB contract | warmup 5, repeat 60 | 118.637 ms/query | 118.597 ms | 7.118 s hot loop | 2.58x hot, 2.58x native | Query points stay in GPU device memory; this is the fair RTDL RT-vs-Embree count comparison. |
| PIP | RTDL OptiX device-resident segment ids | 5,288,684 device output ids, no host count | warmup 5, repeat 60 | 118.600 ms/query | 118.569 ms | 7.116 s hot loop | n/a | Author-shaped device-output route: writes one closest segment id per query point, no positive-count atomic and no host download. It is still about 16.5x slower than author RT, so the remaining gap is kernel/primitive workload, not host upload or output contract. |
| PIP | RTDL Embree | 3,823,783, exact vs RTDL OptiX | warmup 5, repeat 60 | 305.513 ms/query | 305.443 ms | 19.502 s hot loop | 1.0x | CPU is slower in native traversal; hot-loop gap is smaller because RTDL OptiX still pays Python/native wrapper overhead. |
| Overlay | RayJoin author RT | LSI stable at 181,629; map1 vertex PIP stable at 3,823,783; map0 vertex PIP is nondeterministic | repeat 1 clean run plus diagnostic repeats | n/a | not separated | 7.149 s process elapsed | n/a | Fastest whole overlay, but map0 boundary ties are traversal-order dependent. |
| Overlay | RTDL OptiX | LSI 181,629; vertex PIP map0 7,034,556, map1 3,823,783 | one full overlay run | phase timings below | vertex PIP 0.611 s + 0.127 s | 13.050 s total | 1.44x total; 2.51x/4.07x vertex native | Faster than RTDL Embree, slower than author integrated C++ overlay. |
| Overlay | RTDL Embree | LSI 181,629; vertex PIP map0 7,037,306, map1 3,823,783 | one full overlay run | phase timings below | vertex PIP 1.532 s + 0.517 s | 18.748 s total | 1.0x | Corrected world-space `tfar` pruning made this much faster than the earlier no-prune CPU path. |

## Overlay Native Phases

| Backend | LSI count | Vertex map0 in map1 | Vertex map1 in map0 | Midpoint map0 in map1 | Midpoint map1 in map0 | Total |
|---|---:|---:|---:|---:|---:|---:|
| RTDL OptiX | 181,629 | 7,034,556, traversal 0.611 s | 3,823,783, traversal 0.127 s | 27,465, traversal 0.0185 s | 14,355, traversal 0.0083 s | 13.050 s |
| RTDL Embree | 181,629 | 7,037,306, traversal 1.532 s | 3,823,783, traversal 0.517 s | 27,594, traversal 0.0193 s | 14,579, traversal 0.0737 s | 18.748 s |

## Correctness Findings

LSI is exact and stable for author RT, RTDL OptiX, and RTDL Embree on the County x Zipcode pair.

Standalone PIP is now run with the same RayJoin shared scaling box and `query_map_id=1` contract used by overlay. Under that corrected contract, RTDL OptiX and RTDL Embree both return 3,823,783. The RTDL OptiX path also has a device-resident author-shaped closest-segment-id output mode; that mode deliberately does not emit a positive-face count, matching the author's timed query-output shape.

Overlay vertex PIP map1 is exact across author RT, RTDL OptiX, and RTDL Embree: 3,823,783.

Overlay vertex PIP map0 is not a stable exactness target in the author RT code. Repeated author diagnostic runs produced different positive counts in the same setup, observed from 7,029,784 to 7,032,049. Author-to-author differences were only exterior/non-exterior flips; there were no cases where both runs returned different nonzero face ids.

RTDL map0 disagreements have the same signature. In sampled false positives, false negatives, and author-to-author flips, the selected author segment and selected RTDL segment had exactly equal scaled vertical hit `xsect_y`. When both author and RTDL returned a nonzero face, the face id matched. This means the remaining map0 discrepancy is an equal-height boundary tie and traversal/pruning-order issue, not an unexplained polygon-id mismatch.

## Public Wording Boundary

Safe public claim now:

RTDL has a RayJoin-specialized same-source CDB benchmark path for LSI, PIP, and overlay on both NVIDIA OptiX RT hardware and Embree CPU. On County x Zipcode, LSI is exact against the author code and shows strong RT-core acceleration over Embree. PIP is exact between RTDL OptiX and RTDL Embree under the corrected shared-scale RayJoin contract, with RT cores reducing native traversal by about 2.6x when both sides compute the same positive-face count. A device-resident RTDL OptiX PIP route removes host query-point upload and can also write an author-shaped closest-segment-id column, but it remains much slower than the author's 7.2 ms query path; do not claim author-level PIP performance yet. Overlay is functionally staged and faster on OptiX than Embree, but exact author-equivalence for map0 vertex classification is not claimable because the author RT code itself is nondeterministic on equal-height boundary ties.

Unsafe public claim:

Do not claim full exact polygon-overlay reproduction versus the RayJoin author code yet. Do not claim RTDL PIP matches the author's RT performance yet. The map0 vertex PIP tie behavior must either be reproduced at the author's traversal/grouping level or replaced by a documented deterministic boundary convention, and the remaining author-vs-RTDL PIP performance gap needs a true author-equivalent primitive grouping/kernel reproduction rather than more host-memory adjustments.
