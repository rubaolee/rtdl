# Goal723: Event Hotspot Embree Count Summary Mode

Date: 2026-04-21

## Objective

Continue Embree app optimization after Goal722. `event_hotspot_screening` was a strong candidate because the app only needs per-event neighbor counts and hotspot flags. It does not need full `(query_id, neighbor_id, distance)` rows for the default hotspot result.

## Implementation

Updated:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_event_hotspot_screening.py`

New Embree-only option:

- `--embree-summary-mode rows|count_summary`

The default remains `rows` to preserve the original fixed-radius-neighbor app surface. The new `count_summary` mode uses:

- `rt.fixed_radius_count_threshold_2d_embree(..., threshold=0)`

Because the app searches `events` against itself, the summary subtracts one self-neighbor from each count before applying the hotspot threshold.

## Correctness Evidence

Local macOS:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal723_event_hotspot_embree_summary_test

Ran 2 tests in 0.013s
OK
```

Linux `lestat@192.168.1.20`, isolated checkout `/tmp/rtdl_goal723`:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal723_event_hotspot_embree_summary_test

Ran 2 tests in 0.014s
OK
```

The tests verify:

- the app exposes `count_summary`;
- summary counts match row mode;
- hotspot output matches row mode;
- row output is intentionally empty in summary mode;
- summary row count equals event count.

## Performance Evidence

Harness:

- `/Users/rl2025/rtdl_python_only/scripts/goal723_event_hotspot_summary_perf.py`

Mac JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal723_event_hotspot_summary_perf_local_2026-04-21.json`

Linux JSON:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal723_event_hotspot_summary_perf_linux_2026-04-21.json`

Linux median timing, 3 repeats:

| Copies | Events | Row count | Summary rows | Row mode | Count summary | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1024 | 6144 | 18426 | 6144 | 0.0583s | 0.0429s | 1.36x |
| 4096 | 24576 | 73722 | 24576 | 0.2263s | 0.1744s | 1.30x |

Mac median timing, 3 repeats:

| Copies | Events | Row count | Summary rows | Row mode | Count summary | Speedup |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 1536 | 4602 | 1536 | 0.0071s | 0.0038s | 1.85x |
| 1024 | 6144 | 18426 | 6144 | 0.0227s | 0.0161s | 1.41x |
| 4096 | 24576 | 73722 | 24576 | 0.0921s | 0.0744s | 1.24x |

## Interpretation

This is a real app-level Embree optimization for the default event-hotspot use case. The speedup comes from using an existing native fixed-radius count summary instead of materializing all neighbor rows and counting them in Python.

The row mode remains useful when the user wants inspectable neighbor pairs and distances.

## Release Boundary

Allowed claim:

- `event_hotspot_screening` has an Embree count-summary mode.
- On measured Mac/Linux cases, the count-summary mode is faster than row mode for the default hotspot result.
- Linux app-computation speedup is about `1.30x-1.36x`.

Not allowed:

- Do not claim this applies to service coverage gaps, which still needs clinic ids and load counts.
- Do not claim this is a new native primitive; it reuses the existing fixed-radius count-threshold Embree primitive.
- Do not compare this to full CLI timing unless JSON/oracle phases are included and disclosed.
