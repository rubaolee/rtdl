# Goal1269 Graph Visibility Prepared-Reuse Probe

Date: 2026-05-05

## Summary

Goal1267 showed that graph `visibility_edges` OptiX traversal is already very
fast, while total app time is dominated by OptiX scene preparation and host-side
preparation. Goal1269 adds a local diagnostic probe for the next NVIDIA run:
repeat the prepared any-hit count against the same prepared scene and prepared
ray buffer.

This is not a public speedup claim. It is an internal v1.2 measurement tool for
prepared-scene reuse and amortization.

## New Surface

`examples/rtdl_graph_analytics_app.py` now accepts:

```bash
--visibility-query-repeats N
```

The option is valid only for:

```bash
--backend optix --scenario visibility_edges --output-mode summary
```

It keeps one prepared OptiX blocker scene and one prepared ray buffer alive,
then calls the prepared any-hit count path `N` times.

## Reported Fields

The `visibility_edges` section now includes:

- `visibility_query_repeats`
- `run_phases.query_anyhit_count_sec`
- `run_phases.query_anyhit_count_first_sec`
- `run_phases.query_anyhit_count_mean_sec`
- `run_phases.query_anyhit_count_min_sec`

The existing one-shot fields remain:

- `input_construction_sec`
- `blocker_pack_sec`
- `ray_pack_sec`
- `scene_prepare_sec`
- `ray_prepare_sec`
- `summary_postprocess_sec`

## Next Pod Command

Use this after building the current source on an NVIDIA pod:

```bash
PYTHONPATH=src:. python3 examples/rtdl_graph_analytics_app.py \
  --backend optix \
  --scenario visibility_edges \
  --copies 60000 \
  --output-mode summary \
  --require-rt-core \
  --visibility-query-repeats 100
```

Expected interpretation:

- If `query_anyhit_count_mean_sec` stays near the Goal1267 `~0.0002s` range,
  then graph performance work should target scene reuse across batches.
- If repeated query time grows materially, inspect the prepared ray-buffer and
  OptiX count kernel path before changing the graph lowering.
- Positive public graph speedup wording remains blocked either way until a
  same-contract review explicitly authorizes it.

