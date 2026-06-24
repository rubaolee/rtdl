# Goal726 Segment/Polygon Compact Summary Optimization

Date: 2026-04-21

## Scope

This goal optimizes compact output modes in
`examples/rtdl_segment_polygon_anyhit_rows.py`.

Before this goal, `--output-mode segment_counts` and
`--output-mode segment_flags` computed full `segment_polygon_anyhit_rows`
pair rows and then reduced them in Python. After this goal, compact modes use
the existing RTDL `segment_polygon_hitcount` primitive, so Embree returns one
hit-count row per segment instead of all segment/polygon pair rows.

Rows mode is unchanged.

## Files

- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `tests/goal726_segment_polygon_compact_summary_test.py`
- `scripts/goal726_segment_polygon_compact_summary_perf.py`
- `docs/reports/goal726_segment_polygon_compact_summary_perf_local_2026-04-21.json`
- `docs/reports/goal726_segment_polygon_compact_summary_perf_local_large_2026-04-21.json`
- `docs/reports/goal726_segment_polygon_compact_summary_perf_linux_2026-04-21.json`

## Correctness

The compact modes preserve the same app results:

- `segment_counts` matches counts derived from full pair rows.
- `segment_flags` matches `count > 0` for each segment.
- Embree compact mode matches the CPU Python reference.

Verification commands:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal726_segment_polygon_compact_summary_test \
  tests.goal692_optix_app_correctness_transparency_test

PYTHONPATH=src:. python3 scripts/goal410_tutorial_example_check.py \
  --machine local \
  --output /tmp/goal726_goal410_local.json

python3 -m py_compile \
  scripts/goal726_segment_polygon_compact_summary_perf.py \
  examples/rtdl_segment_polygon_anyhit_rows.py
```

Results:

- Focused unit tests: `7` tests passed locally.
- Goal410 local harness: passed.
- Python compile check: passed.
- Linux focused tests: `7` tests passed.

## Performance

The comparison is between:

- `rows`: full `segment_polygon_anyhit_rows` pair-row mode
- `segment_counts`: compact mode backed by `segment_polygon_hitcount`

Mac local large run:

| Copies | Rows best sec | Compact best sec | Speedup | Rows emitted | Compact rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1024 | 0.0230 | 0.0183 | 1.26x | 11264 | 10240 |
| 4096 | 0.0918 | 0.1132 | 0.81x | 45056 | 40960 |
| 16384 | 0.4792 | 0.3371 | 1.42x | 180224 | 163840 |

Mac geomean speedup: `1.13x`.

Linux run:

| Copies | Rows best sec | Compact best sec | Speedup | Rows emitted | Compact rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1024 | 0.0530 | 0.0422 | 1.26x | 11264 | 10240 |
| 4096 | 0.2624 | 0.1718 | 1.53x | 45056 | 40960 |
| 16384 | 1.1844 | 1.2090 | 0.98x | 180224 | 163840 |

Linux geomean speedup: `1.23x`.

## Boundary

This is a compact-output optimization for
`rtdl_segment_polygon_anyhit_rows.py --output-mode segment_counts` and
`--output-mode segment_flags`.

It is not a universal segment/polygon speedup. Full `rows` mode still emits
pair rows and remains the correct mode when users need polygon ids.

## Verdict

ACCEPT. The change removes unnecessary pair-row materialization for compact
outputs and gives modest measured improvement on Linux/Mac large tiled cases,
while preserving row mode and existing RT-core performance honesty wording.
