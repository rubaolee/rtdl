# Goal4468 V3.0 M72 Triangle Unique-Weighted Segment Rays

Goal4468 tests the next Triangle Counting V3 optimization after Goal4467:
replace physically duplicated two-hop rays with unique `(src, dst)` rays plus
uint64 weights inside each segment.

The RTDL engine contract is unchanged. The engine still sees generic 3-D rays,
generic 3-D triangles, and weights through the existing weighted any-hit
summary primitive. The graph-specific work stays in the CuPy app partner.

## Result Table

All rows use warmup=1, repeat=3, the same dataset and cap settings as Goal4467
unless noted.

| Dataset | Count | Logical rays | Unique-weighted rays | Ray compression | Total duplicate | Total unique | Query speedup | Ray-build cost | Build+query speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 177,820,130 | 928,731,472 | 528,793,097 | 1.76x | 14.153s | 14.073s | 2.36x | 2.44x slower | 1.11x |
| `soc-LiveJournal1` | 285,730,264 | 1,383,299,326 | 750,099,466 | 1.84x | 25.747s | 25.105s | 2.47x | 2.44x slower | 1.13x |
| `com-orkut` | 627,584,181 | 8,579,930,671 | 4,759,226,031 | 1.80x | 115.032s | 116.527s | 2.42x | 2.50x slower | 1.13x |

## Reading

This is a real representation improvement, but not yet a whole-route win.

The good part: unique-weighted segment rays cut physical ray count by
1.76x-1.84x and improve RT traversal median by 2.36x-2.47x. That directly
attacks the Goal4467 traversal debt.

The bad part: each segment now pays a CuPy `unique(return_counts=True)` cost to
compress duplicate two-hop keys. That makes segment ray construction
2.44x-2.50x slower. The net median build+query phase improves only
1.11x-1.13x, and the formal total is only slightly better on `com-lj` and
`soc-LiveJournal1`, while `com-orkut` is slightly worse.

The 20M `com-orkut` unique-weighted probe completed, unlike the duplicate-ray
20M query that was unsafe in Goal4466, but it was not faster than the 15M
unique-weighted probe. The measured setting remains 15M on this RTX 4000 Ada
pod.

## Implementation Boundary

Allowed:

- Explicit `--segment-ray-representation unique_weighted` experiments.
- Current-route wording that unique-weighted rays reduce traversal pressure.
- Current-route wording that partner compression is now the bottleneck.

Blocked:

- Public triangle-count RT-core speedup wording.
- Claiming RTDL beats cuGraph.
- Claiming RTDL beats authors pure count kernels.
- Hiding unique-weighted as an automatic default.
- Adding graph-specific native engine logic.

## Next Action

The next optimization target is not more cap tuning. It is cheaper or reusable
unique two-hop compression:

- prepared compressed segment ray batches for repeated runs;
- a segmented device-side RLE/unique partner path that reduces temporary
  materialization cost;
- or a more generic weighted-key stream primitive that preserves the same
  engine boundary without graph-specific native callbacks.

## Evidence

- `docs/reports/goal4468_v3_0_m72_triangle_unique_weighted_comparison_packet_2026-06-16.json`
- `docs/reports/goal4468_v3_0_m72_triangle_unique_weighted_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4468_v3_0_m72_triangle_unique_weighted_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4468_v3_0_m72_triangle_unique_weighted_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4468_v3_0_m72_triangle_unique_weighted_com_orkut_20m_probe_w0r1_2026-06-16.json`
- `docs/reports/goal4467_v3_0_m71_triangle_current_comparison_packet_2026-06-16.json`
