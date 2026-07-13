# Goal4973 — Exact LSI Producer And Downstream Floor Cost Decomposition

Date: 2026-07-04

## Purpose

Goal4972 closed the count-pass hypothesis:

- exact pair-id device columns: `2.687378019094467s`
- bounded exact pair-id device columns: `2.688651569187641s`
- removable count pass: about `0.002s`

But the native timing inside the bounded route reports only about `0.0023s` of output traversal/write
work. Therefore the first problem is the unaccounted difference:

```text
Python phase for bounded exact LSI ~= 2.6887s
native output traversal/write      ~= 0.0023s
unaccounted                         ~= 2.6864s
```

The midcheck review also pointed out a second, equally important fact from the prepared replay route:

```text
fresh bounded route       ~= 5.2776s = LSI 2.6887s + downstream ~2.589s
prepared replay route     ~= 2.5691s = LSI 0.0090s + downstream ~2.560s
```

Therefore the `~2.686s` LSI gap is probably one-time / amortizable setup, while the `~2.56s`
downstream floor is persistent. Goal4973 must decompose both, otherwise we risk optimizing the
amortizable setup and leaving the real steady-state operator stuck at `~2.56s`.

## Working Hypothesis

The LSI missing time is likely one or more of:

1. runtime pipeline compilation / NVCC fallback cost
2. OptiX module/pipeline/SBT setup cost
3. prepared/grouped-range acceleration setup hidden outside current timers
4. CUDA context / stream synchronization placement
5. repeated per-process initialization caused by the measurement harness

The persistent downstream floor is likely one or more of:

1. reprojection
2. map0/map1 sort
3. vertex PIP host-facing wrapper / row return
4. midpoint generation and midpoint PIP
5. carrier construction
6. small downstream consumer

The goal is to measure both phase families directly, not guess.

## Work

1. Add native phase timing around the exact LSI producer setup path:
   - scaled segment cache ensure
   - grouped range ensure
   - exact-count pipeline ensure/compile
   - split-pair-id kernel ensure
   - OptiX launch time
   - split kernel time
   - DtoH copy time for result columns
2. Add a same-process repeated-run diagnostic:
   - first bounded exact run
   - second bounded exact run on same prepared query
   - third bounded exact run after workspace preparation
3. Add a downstream steady-state decomposition table for the prepared replay route:
   - reprojection
   - sort map0
   - sort map1
   - vertex PIP map0 in map1
   - vertex PIP map1 in map0
   - midpoint points side0/side1
   - midpoint PIP side0/side1
   - midpoint face assignment
   - grouped carrier construction
   - downstream consumer
4. Explicitly separate:
   - one-time / amortizable setup cost
   - per-overlay fresh cost
   - prepared/replay steady-state cost
5. Run the top4 representative with:
   - exact pair-id device columns
   - bounded exact pair-id device columns
   - same-process repeated bounded exact diagnostic
   - prepared replay downstream decomposition
6. Preserve correctness gates:
   - `428322` LSI rows
   - xsect side0/side1 `428322 / 428322`
   - vertex positives `812721 / 4527305`
   - device order validation true

## Genericity Rules

- Only measure/optimize generic planar-map LSI pair-id production.
- Core output remains `{left_id, right_id}` device columns.
- No RayJoin output-chain logic in core.
- No author text format logic in core.
- No Layer 4 callback/fusion claim.

## Decision Gates

If pipeline/module compilation dominates the LSI missing time:

- Next goal should build a reusable exact LSI pipeline/session cache contract.
- Do not claim traversal speedup.

If grouped-range/prepared workspace setup dominates the LSI missing time:

- Next goal should make workspace preparation explicit and reusable for fresh binary operator usage.

If OptiX launch/traversal dominates after setup is warm:

- Next goal should target exact LSI predicate/traversal implementation.

If DtoH or Python copying dominates the LSI route:

- Next goal should resume resident downstream work.

If persistent downstream floor remains around `~2.56s` after LSI setup is amortized:

- Next goal must target the largest downstream phase, not more LSI setup work.
- Likely candidates are midpoint generation/PIP, vertex PIP wrapper, or carrier construction.
- Do not declare the binary operator competitive merely because LSI replay is cheap.

## Exit Labels

- `exact_lsi_cost_dominated_by_pipeline_compile`
- `exact_lsi_cost_dominated_by_workspace_setup`
- `exact_lsi_cost_dominated_by_traversal`
- `exact_lsi_cost_dominated_by_host_copy`
- `steady_state_cost_dominated_by_downstream_floor`
- `blocked_by_measurement_instrumentation_failure`

## Not Authorized

- No performance headline.
- No author comparison.
- No RayJoin-specific kernel.
- No public release wording.
- No implementation beyond timing instrumentation unless the phase table identifies the bottleneck.
