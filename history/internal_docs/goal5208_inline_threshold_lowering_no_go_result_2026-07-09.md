# Goal5208 Inline Threshold Lowering No-Go Result

Date: 2026-07-09

## Verdict

```text
completed_inline_threshold_lowering_no_go__keep_inline512_default
```

## Purpose

Goal5207 made the same-process warm route explicit and showed the current
steady floor:

```text
measured warm route ~= 0.626s
frontier_rows phase ~= 0.405s
native total ~= 0.396s
OptiX launch / inline scan ~= 0.373s
frontier rows = 0
```

Goal5208 tested whether lowering the generic `max_inline_points` threshold
could improve the steady native inline scan by offloading some dense cells back
to the continuation path.

This is a route-local tuning / no-go goal. It does not change RTDL core and does
not claim paper performance reproduction.

## Method

All runs used the same full-public Stanford Dragon -> HappyBuddha Level-B pair,
the Goal5207 explicit warmup protocol, and the Goal5188 author summary:

```text
source_limits = all
route_warmup_source_limit = all
skip_exact_oracle = true
grid_shape = 32,32,32
initial_state = local-grid-cell
frontier_inline_nearest = true
collect_frontier_native_phase_timings = true
```

Thresholds tested:

```text
512  baseline from Goal5207
384
256
128
```

Artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5207_explicit_warmup_all_then_measured_all_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5208_inline384_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5208_inline256_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5208_inline128_warm_protocol_graphics_dragon_happy_buddha_2026-07-08.json
```

## Results

Measured case only; warmup case is excluded from summary statistics.

| `max_inline_points` | matched | measured route | measured case total | frontier rows | native total | OptiX launch | nearest continuation | full run total incl. load+warmup+measured |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 512 | true | 0.625589s | 0.808628s | 0 | 0.395595s | 0.372937s | 0.000786s | 2.892787s |
| 384 | true | 0.622555s | 0.802632s | 16,502 | 0.394094s | 0.370426s | 0.016575s | 2.954290s |
| 256 | true | 0.671155s | 0.848346s | 146,548 | 0.381632s | 0.359667s | 0.041957s | 2.976448s |
| 128 | true | 1.064760s | 1.244300s | 1,286,627 | 0.403469s | 0.317101s | 0.403612s | 3.837072s |

## Interpretation

Lowering the threshold can reduce the native OptiX inline launch/scan time, but
it does so by materializing frontier rows and pushing work into the generic
continuation path.

The tradeoff is unfavorable:

- `384` is only about 3ms faster in measured route wall than `512`, within
  route noise, and the full run including warmup is worse.
- `256` lowers OptiX launch by about 13ms but adds about 41ms continuation and
  makes measured route slower.
- `128` lowers OptiX launch by about 56ms but emits about 1.29M frontier rows
  and makes continuation about 0.404s; route becomes much slower.

The current default remains:

```text
max_inline_points = 512
```

At this representative full-public input, the better strategy is to keep dense
cells inline rather than offload them to continuation rows.

## Claim Boundary

This goal claims:

- all tested lower thresholds preserved the Level-B HDResult match;
- lowering `max_inline_points` did not produce a meaningful route improvement;
- `512` remains the current evidence-backed default.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- a new RTDL optimization;
- that the warm measured route replaces the one-shot fresh route.

## Next

Do not reopen lower inline-threshold tuning without new evidence or a different
execution model.

The remaining steady floor is still the native inline nearest scan / work
ordering itself:

```text
OptiX launch / inline scan ~= 0.37s at inline512
```

Further performance work must change that execution model or introduce a more
effective generic prepared runtime / spatial work-ordering strategy, rather than
moving dense-cell work into row continuation.
