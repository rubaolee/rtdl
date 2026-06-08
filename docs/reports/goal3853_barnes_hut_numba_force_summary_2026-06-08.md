# Goal3853: Barnes-Hut Numba Force-Summary Repeat Accounting

Date: 2026-06-08

Status: implemented and A5000-validated

## Purpose

The current Barnes-Hut scale-profile row uses the Numba partner exact-force
reference path:

```bash
python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode partner_exact_force --partner numba --force-output-mode force_summary \
  --body-count 8192 --skip-validation --repeat 3 --warmup 1
```

Before Goal3853, the wrapper accepted `--repeat` / `--warmup` but did not pass
them into the `partner_exact_force` app path. The `force_summary` path also
materialized Python force-row dictionaries before reducing them to checksums.

Goal3853 makes the command honest and lighter:

- `partner_exact_force` now forwards `query_repeat` and `warmup`;
- `force_summary` with `--skip-validation` prepares partner columns once,
  repeats the generic Numba pairwise force kernel, and reports the measured
  median hot kernel time;
- `force_summary` avoids Python per-body force-row dictionaries and only
  materializes the final checksum summary;
- no native engine ABI or Barnes-Hut-specific native logic is added.

## A5000 Evidence

Artifact directory:

- `docs/reports/goal3853_barnes_hut_numba_force_summary_a5000/`

Direct payload:

| Metric | Value |
| --- | ---: |
| bodies | `8192` |
| partner | `numba` |
| strategy | `block_source_target_stride_512_reduce_fastmath_true` |
| median force kernel | `0.008967613` |
| summary materialization | `0.000258761` |
| repeat / warmup | `3 / 1` |
| materializes Python force rows | `false` |

The file-backed current scale-profile runner also passed the Barnes-Hut row:

| Metric | Value |
| --- | ---: |
| runner status | `pass` |
| runner process elapsed | `1.751682193` |
| stdout JSON parseable | `true` |
| claim-boundary violations | `0` |

## Interpretation

This goal does not produce a large cold-process wall-clock improvement. Instead
it shows that the current Barnes-Hut Numba force kernel is already a very small
part of the command-line row: about `9 ms` for the measured 8192-body hot force
kernel, while the full process remains about `1.75 s` because import, Numba CUDA
JIT/setup, body generation, and Python process startup dominate.

That changes the next engineering target. Barnes-Hut should not spend the next
round on another all-pairs Numba force kernel micro-optimization unless a larger
fixture exposes a new kernel bottleneck. The better future target is cold-start
and residency: kernel caching, persistent prepared sessions, or a larger
resident benchmark harness.

## Boundary

This is an app-level Numba partner improvement and accounting fix. It is not an
RT-core claim, not a Barnes-Hut paper reproduction, not a public speedup claim,
and not release authorization.

