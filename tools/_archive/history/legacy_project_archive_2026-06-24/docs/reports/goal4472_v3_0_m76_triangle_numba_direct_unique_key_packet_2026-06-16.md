# Goal4472 V3.0 M76 Triangle Numba Direct Unique-Key Builder

Goal4472 tests the first concrete M75 follow-up: can we make unique-key
compression cheaper without adding graph-specific native engine logic?

Implementation: add an explicit `--segment-unique-key-builder numba_direct`
route. It uses a no-C++ Numba CUDA kernel to fill packed `(src, dst)` two-hop
keys directly, then uses the same CuPy `unique(return_counts=True)` reduction
and the same generic RTDL weighted any-hit primitive. The existing route remains
`--segment-unique-key-builder cupy_repeat`.

## Result Table

All rows use `unique_weighted`, `prepared_segment_replay`, warmup=1, repeat=3,
15M ray cap, and the same RTX 4000 Ada pod. The table compares same-commit
`cupy_repeat` and `numba_direct` artifacts.

| Dataset | Total speedup | Backend speedup | Build-once speedup | Segment-ray build speedup | Query median change |
| --- | ---: | ---: | ---: | ---: | ---: |
| `com-lj` | 1.03x | 1.05x | 1.11x | 1.17x | 0.933s -> 0.897s |
| `soc-LiveJournal1` | 0.98x | 1.03x | 1.25x | 1.36x | 1.285s -> 1.370s |
| `com-orkut` | 1.07x | 1.09x | 1.57x | 1.64x | 8.178s -> 8.577s |

Counts match between `cupy_repeat` and `numba_direct` for all rows:
177,820,130; 285,730,264; 627,584,181.

## Reading

The direct Numba key-fill idea works for the intended bottleneck:

- segment-ray build improves on all rows by 1.17x-1.64x;
- build-once improves on all rows by 1.11x-1.57x;
- measured backend phase improves on all rows by 1.03x-1.09x.

But end-to-end total is not universally better: `soc-LiveJournal1` total is
0.98x because non-backend graph-contract/plan time and query median moved
against the route in this single same-commit run. Therefore M76 is useful
engineering evidence, not a default-route promotion.

Current decision: keep `numba_direct` as an explicit key-builder option. Do not
make it hidden default. The next useful target is query-side variance/regression
or a reusable prepared ray-batch API, not more batch-cap tuning.

## Claim Boundary

Allowed:

- Internal current-route wording that `numba_direct` reduces segment-ray build
  and backend time in this same-commit large-row packet.
- Explicit user selection of `--segment-unique-key-builder numba_direct`.

Blocked:

- Public triangle-count RT-core speedup wording.
- Hidden automatic key-builder selection.
- RTDL beats cuGraph wording.
- Whole-app acceleration wording.
- Graph-specific native engine callbacks or app-specific native ABI.

## Evidence

- `docs/reports/goal4472_v3_0_m76_triangle_numba_direct_unique_key_packet_2026-06-16.json`
- `docs/reports/goal4472_v3_0_m76_triangle_cupy_repeat_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4472_v3_0_m76_triangle_numba_direct_com_lj_w1r3_2026-06-16.json`
- `docs/reports/goal4472_v3_0_m76_triangle_cupy_repeat_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4472_v3_0_m76_triangle_numba_direct_soc_livejournal1_w1r3_2026-06-16.json`
- `docs/reports/goal4472_v3_0_m76_triangle_cupy_repeat_com_orkut_w1r3_2026-06-16.json`
- `docs/reports/goal4472_v3_0_m76_triangle_numba_direct_com_orkut_w1r3_2026-06-16.json`
