# Goal5198 Grid-Shape Telemetry / No-Go Result

## Status

`implemented_review_pending`

Goal5198 is a measurement gate for the current X-HD full-public Level-B
Dragon/HappyBuddha route. It does not change RTDL code. It reruns the generic
cell-MBR route with native inline-nearest telemetry across grid shapes to test a
simple hypothesis:

> Can we reduce the remaining native inline-nearest floor by making target grid
> cells finer?

The answer is **no for this route**. Finer grids reduce inline point-distance
evaluations, but they increase occupied-cell count, local-grid seed probes, and
inline cell hits enough that route wall gets worse. Coarser `24^3` does not
complete the empty-frontier inline route under `frontier_row_capacity=0`.

## Why This Goal Exists

After Goal5197, the current best full-public Level-B route remains about
`2.25-2.28s`:

```text
seed ~= 0.55s
native frontier / inline ~= 0.93s
frontier_rows = 0
nearest_continuation ~= 0.016s
```

The remaining native floor is not Python continuation. Goal5198 measures the
native inline work under alternative generic grid shapes before adding more code.

## POD

```text
host = 213.173.108.24
port = 13502
preflight = POD_OK
GPU = NVIDIA RTX 4000 Ada Generation
```

All successful runs used:

```text
source = public Stanford Dragon, all 437645 points
target = public Stanford HappyBuddha, all 543652 points
author_hd_result = 0.12572988867759705
backend = optix
source_selection_policy = evenly-spaced
translate_each_input_to_min_bound = true
initial_state = local-grid-cell
max_inline_points = 512
frontier_inline_nearest = true
collect_inline_stats = true
frontier_row_capacity = 0
skip_exact_oracle = true
author_tolerance = 1e-6
```

The zero row capacity is intentional and fail-closed. A run succeeds only if the
native inline route resolves all queries without emitting frontier rows.

## Results

| Grid | Match | Route wall | Seed | Native frontier / inline | Grid MBRs | Inline cell hits | Inline point evals | Notes |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `24^3` | n/a | n/a | n/a | n/a | n/a | n/a | n/a | fail-closed overflow: `155511` frontier rows attempted with capacity `0` |
| `32^3` | true | `2.240s` | `0.549s` | `0.932s` | `0.179s` | `3,641,962` | `400,610,300` | current default grid |
| `48^3` | true | `3.162s` | `0.696s` | `1.704s` | `0.187s` | `4,817,941` | `240,461,433` | fewer point evals, but more hit/seed overhead |
| `64^3` | true | `6.759s` | `0.967s` | `4.585s` | `0.193s` | `5,997,611` | `165,882,750` | much slower |
| `128^3` | true | `10.722s` | `5.222s` | `4.722s` | `0.203s` | `7,763,318` | `63,642,264` | much slower |

Key interpretation:

- Finer grids lower `inline_point_evaluation_count`.
- But they increase occupied cells and inline cell hits, and the local-grid seed
  probes far more grid cells.
- On this workload, the overhead of more cells dominates the savings from fewer
  point evaluations.
- `32^3` remains the current default among tested generic grid shapes.

## Artifacts

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_current_goal5198_telemetry_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5198_grid_48x48x48_telemetry_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5198_grid_64x64x64_telemetry_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5198_grid_128x128x128_telemetry_graphics_dragon_happy_buddha_2026-07-08.json
```

The failed `24^3` run did not produce a result JSON; its fail-closed error was:

```text
OptiX cell-MBR nearest frontier 3D output overflowed; attempted 155511; capacity 0;
failure_mode=fail_closed_overflow; partial_result_returned=False
```

## Claim Boundary

Authorized:

- route-local Level-B telemetry on public Stanford Dragon/HappyBuddha;
- statement that `32^3` remains the current default among tested shapes;
- statement that finer grid shapes are no-go for this route under the tested
  parameters.

Not authorized:

- author-vs-RTDL performance ratio;
- exact paper dataset reproduction;
- full X-HD paper reproduction;
- claim that grid shape tuning is universally solved;
- claim that 32^3 is optimal beyond the tested route and public input pair.

## Next

Grid-shape tuning alone should not be the next performance path. The remaining
hard problem is the generic native inline-nearest collector execution model:
`~3.6M` inline cell hits and `~400M` point-distance evaluations remain at the
current default. A real next implementation should either:

1. change how those per-cell point scans are parallelized, or
2. introduce a stronger generic spatial index / traversal primitive that reduces
   cell hits without exploding seed cost.
