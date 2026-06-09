# Goal4229 Barnes-Hut Force-Summary Aggregate Timing

Date: 2026-06-09

Status: internal measurement-contract hardening accepted with boundary

## Purpose

The current Barnes-Hut benchmark row uses the generic partner exact-force
summary route with Numba. The route was already functional, but its metadata
only exposed the median force-kernel time and repeat count. That made
long-repeat evidence depend on a median-times-repeat proxy instead of a direct
aggregate timing field.

Goal4229 hardens the benchmark app's measurement contract without changing the
native engine or the force algorithm:

- `prepared_force_repeat_protocol.force_kernel_runs_sec`
- `prepared_force_repeat_protocol.force_kernel_total_sec`
- existing `median_force_kernel_sec`

## Pod Result

Artifact root:
`docs/reports/goal4229_barnes_hut_numba_long_repeat_rtx4000ada/`

Command shape:

```bash
python examples/v2_0/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py \
  --mode partner_exact_force \
  --partner numba \
  --force-output-mode force_summary \
  --body-count 8192 \
  --skip-validation \
  --repeat 200 \
  --warmup 3
```

| Field | Value |
| --- | ---: |
| source commit | `21d5af1d` |
| GPU | `NVIDIA RTX 4000 Ada Generation` |
| measured iterations | `200` |
| recorded run count | `200` |
| median force kernel sec | `0.008580248802900314` |
| total force kernel sec | `1.7285085022449493` |
| one-second hot-path floor met | `true` |
| materializes Python force rows | `false` |
| prepared partner columns reused | `true` |
| prepared output columns reused | `true` |

## Interpretation

This closes the Barnes-Hut measurement-floor ambiguity for the current
force-summary row. The benchmark remains a generic partner exact-force /
grouped-vector-reduction reference lane, not a full RT-BarnesHut paper
reproduction and not a native force-law primitive.

## Boundary

Goal4229 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.

It is not a public speedup claim.
