# Goal5209 Cell Order Work-Ordering No-Go Result

Date: 2026-07-09

## Verdict

```text
completed_cell_order_work_ordering_no_go__keep_native_cell_order_default
```

## Purpose

After Goal5208, the remaining steady floor stayed in native inline nearest
scan/work ordering:

```text
inline512 measured route ~= 0.626s
OptiX launch / inline scan ~= 0.37s
frontier rows = 0
```

Goal5209 tested whether changing the generic cell primitive ordering before
native cell-MBR traversal could influence OptiX BVH / any-hit order enough to
find closer current-best witnesses earlier.

This is app-owned route orchestration only. No RTDL core or native code was
changed.

## Implementation

Changed:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5209_cell_order_work_ordering_test.py
```

New CLI:

```text
--cell-order native
--cell-order point-count-asc
--cell-order point-count-desc
```

The ordering reorders generic cell columns before frontier traversal while
preserving cell IDs, point offsets, and point counts. The default remains:

```text
--cell-order native
```

## Validation

Local:

```text
py -m unittest \
  tests.goal5209_cell_order_work_ordering_test \
  tests.goal5207_explicit_route_warmup_protocol_test \
  tests.goal5187_xhd_full_public_route_only_gate_test

Ran 7 tests OK

py_compile = OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

py_compile = OK
tests.goal5207_explicit_route_warmup_protocol_test + tests.goal5187... = OK
```

## POD Evidence

Same full-public Stanford Dragon -> HappyBuddha Level-B workload and same
Goal5207 explicit warmup protocol:

```text
source_limits = all
route_warmup_source_limit = all
max_inline_points = 512
frontier_inline_nearest = true
collect_frontier_native_phase_timings = true
```

Single exploratory runs:

| cell order | matched | measured route | measured case total | full run total | native total | OptiX launch |
|---|---|---:|---:|---:|---:|---:|
| native baseline | true | 0.625589s | 0.808628s | 2.892787s | 0.395595s | 0.372937s |
| point-count-asc | true | 0.618405s | 0.800511s | 2.876901s | 0.394693s | 0.372384s |
| point-count-desc | true | 0.647470s | 0.827100s | 2.897721s | 0.422545s | 0.370868s |

Repeat runs, measured case only:

| cell order | route median | route min | route max | case-total median |
|---|---:|---:|---:|---:|
| native | 0.615933s | 0.601413s | 0.616578s | 0.797471s |
| point-count-asc | 0.614551s | 0.602770s | 0.618173s | 0.798096s |

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_point_count_asc_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_point_count_desc_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_native_repeat1_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_native_repeat2_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_native_repeat3_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_point_count_asc_repeat1_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_point_count_asc_repeat2_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5209_cell_order_point_count_asc_repeat3_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
```

## Interpretation

`point-count-asc` is not strong enough to become the default:

```text
native median route        ~= 0.615933s
point-count-asc median     ~= 0.614551s
median movement            ~= 0.0014s
```

That movement is route noise, not a credible optimization. The case-total
median is also not better.

`point-count-desc` is a clear no-go: it preserves correctness but makes native
total and route wall worse.

The default remains:

```text
cell_order = native
max_inline_points = 512
```

The `--cell-order` flag remains an experimental diagnostic route switch only.

## Claim Boundary

This goal claims:

- cell-order variants preserve correctness on the Level-B full-public pair;
- point-count ordering is not a meaningful route optimization;
- native cell order remains the current default.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- a new RTDL core optimization;
- a warm-only headline.

## Next

Do not reopen static point-count cell ordering without new evidence.

The next meaningful route attack must change the native inline-nearest execution
model itself or introduce a stronger generic prepared/runtime spatial strategy.
