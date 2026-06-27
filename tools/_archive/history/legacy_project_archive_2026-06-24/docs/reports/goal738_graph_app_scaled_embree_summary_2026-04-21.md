# Goal738 Graph App Scaled Embree Summary

Date: 2026-04-21

## Scope

Goal738 makes the public graph app usable for Embree app-performance
characterization without changing its beginner-facing default behavior.

Changed files:

- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_bfs.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_triangle_count.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_graph_analytics_app.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal714_embree_app_thread_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal738_graph_app_scaled_summary_test.py`
- `/Users/rl2025/rtdl_python_only/docs/application_catalog.md`

## User-Facing Change

The default commands remain unchanged:

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_bfs.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_graph_triangle_count.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py --backend cpu_python_reference
```

New scalable mode:

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py \
  --backend embree \
  --copies 1024 \
  --output-mode summary
```

`--copies N` repeats the deterministic graph fixtures with disjoint vertex ID
ranges. `--output-mode summary` emits compact BFS discovery counts and
triangle counts instead of full row lists.

## Correctness

Local focused validation:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal686_app_catalog_cleanup_test \
  tests.goal513_public_example_smoke_test \
  tests.goal401_v0_6_large_scale_engine_perf_gate_test \
  -v
```

Result: `18 tests OK`.

Additional Goal738 tests validate:

- BFS scaled summary counts.
- Triangle scaled summary counts.
- Default unified graph app row-emitting behavior.
- Embree summary parity with CPU reference when Embree is available.

## macOS Embree Evidence

Command:

```bash
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py \
  --apps graph_analytics \
  --copies 1024 \
  --threads 1,auto \
  --warmups 1 \
  --min-sample-sec 0.5 \
  --max-repeats 8 \
  --output docs/reports/goal738_graph_embree_scaled_app_perf_macos_2026-04-21.json
```

Result file:

`/Users/rl2025/rtdl_python_only/docs/reports/goal738_graph_embree_scaled_app_perf_macos_2026-04-21.json`

Observed app-level wall-clock result on this Mac:

| Copies | CPU reference elapsed | Embree 1 thread median | Embree auto median | Auto vs 1 thread |
| --- | ---: | ---: | ---: | ---: |
| 1024 | 0.136 s | 0.140 s | 0.139 s | 1.01x |

Exploratory 4096-copy run:

| Copies | CPU reference elapsed | Embree 1 thread median | Embree auto median | Auto vs 1 thread |
| --- | ---: | ---: | ---: | ---: |
| 4096 | 0.160 s | 0.194 s | 0.188 s | 1.03x |

## Honest Boundary

This change improves the public graph app surface and enables larger,
repeatable graph fixtures. It does not claim that the current Embree graph
path is already a strong multicore speedup. Current app-level measurements are
still dominated by Python process startup, JSON handling, and a native graph
implementation that has limited parallel benefit for these compact repeated
fixtures.

The useful release claim is narrower:

- The graph app can now run scalable deterministic fixtures.
- Embree results match CPU reference summaries.
- Embree is executing the existing CPU BVH/point-query graph path.
- More native graph optimization is still needed before claiming strong Embree
  graph app performance.
