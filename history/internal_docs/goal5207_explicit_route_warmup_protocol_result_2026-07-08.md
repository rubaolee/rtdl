# Goal5207 Explicit Route Warmup Protocol Result

Date: 2026-07-08

## Verdict

```text
completed_explicit_route_warmup_protocol__warm_metric_separated_from_fresh
```

## Purpose

Goal5206 showed a major first-use vs same-process warm gap:

```text
fresh one-shot route ~= 1.16-1.17s
same-process second route ~= 0.61s
```

Before Goal5207, that warm behavior could only be observed with ad hoc
near-duplicate source-limit sequences like `all,437644`. Goal5207 adds an
explicit warmup protocol to the full-public X-HD gate so warm-route evidence can
be measured without hiding preparation / first-use cost.

## Implementation

Changed `run_xhd_full_public_subset_scaling_gate.py`:

- added CLI flag:

```text
--route-warmup-source-limit <positive-int|all>
```

- executes the warmup case before measured cases;
- records the warmup under top-level `route_warmup`;
- marks it:

```text
case_role = "warmup"
excluded_from_summary_statistics = true
```

- excludes it from measured `cases` and summary statistics;
- records top-level:

```text
route_warmup_source_limit
phase_timings_sec.route_warmup
summary_statistics.route_warmup_used
route_feasibility.route_warmup_excluded_from_summary_statistics
claim_boundary.route_warmup_used
```

No RTDL core code was changed. This is a paper-app performance protocol change.

## Validation

Local:

```text
py -m unittest \
  tests.goal5207_explicit_route_warmup_protocol_test \
  tests.goal5187_xhd_full_public_route_only_gate_test \
  tests.goal5205_fast_ascii_ply_matrix_loader_test \
  tests.goal5203_numpy_point_matrix_input_loader_test

Ran 13 tests OK

py_compile = OK
```

POD:

```text
host = 213.173.108.24
port = 13502
gpu = NVIDIA RTX 4000 Ada Generation
driver = 550.127.05

same 13 tests OK
```

## Full-Public Warm Protocol Evidence

Artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5207_explicit_warmup_all_then_measured_all_graphics_dragon_happy_buddha_2026-07-08.json
```

Run settings:

```text
source_limits = all
route_warmup_source_limit = all
skip_exact_oracle = true
author_summary = Goal5188 author full-public summary
```

Warmup case:

```text
source_limit = 437645
case_role = warmup
excluded_from_summary_statistics = true
matched = true
rtdl_route_wall ~= 1.176s
case_total ~= 1.389s
frontier_rows ~= 0.741s
initial_state_seed ~= 0.237s
native_total ~= 0.596s
optix_launch ~= 0.376s
```

Measured case:

```text
source_limit = 437645
case_role = measured
matched = true
rtdl_route_wall ~= 0.626s
case_total ~= 0.809s
frontier_rows ~= 0.405s
initial_state_seed ~= 0.032s
native_total ~= 0.396s
optix_launch ~= 0.373s
```

Top-level timing:

```text
load_full_inputs ~= 0.685s
route_warmup ~= 1.389s
total ~= 2.893s
```

Summary statistics use only the measured case:

```text
median_route_wall_sec ~= 0.626s
route_warmup_used = true
```

## Interpretation

Goal5207 makes two regimes explicit:

```text
Fresh one-shot route:
  route ~= 1.16-1.17s
  total ~= 2.06s

Warm measured route after explicit same-process warmup:
  warmup case_total ~= 1.389s
  measured route ~= 0.626s
  measured case_total ~= 0.809s
  full run total including load + warmup + measured ~= 2.893s
```

The warm route is a valid measurement only when reported with the warmup /
first-use cost. It must not replace the fresh one-shot headline.

## Claim Boundary

This goal claims:

- a clean performance protocol for explicit same-process route warmup;
- warmup and measured cases are separated in artifacts;
- summary statistics exclude warmup;
- the current Level-B route still matches the Goal5186 author HDResult.

This goal does not claim:

- exact paper dataset reproduction;
- full X-HD paper reproduction;
- author-vs-RTDL performance ratio;
- author performance parity;
- that `~0.626s` is the default one-shot result;
- a new RTDL optimization.

## Next

The performance matrix can now honestly report:

```text
one-shot route ~= 1.16-1.17s
one-shot total ~= 2.06s
warmup cost ~= 1.39s
warm measured route ~= 0.626s
warm measured case_total ~= 0.809s
```

The next implementation work should either:

1. attack the steady native inline scan (`optix_launch ~=0.37s`) through a
   stronger generic spatial execution model; or
2. build a more formal generic prepared runtime API beyond this app-owned
   warmup measurement protocol.
