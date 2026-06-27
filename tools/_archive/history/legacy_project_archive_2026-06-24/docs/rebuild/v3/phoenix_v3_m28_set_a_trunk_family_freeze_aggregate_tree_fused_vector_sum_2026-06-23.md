# Phoenix V3 M28 Set-A Runtime-Trunk Family Freeze

Date: 2026-06-23
Status: `candidate_family_frozen_pending_external_review`

## Decision

Freeze the first true Set-A Phoenix V3 runtime-trunk family as:

`generic aggregate-tree fused weighted-vector sum 2D, explicit Numba CUDA partner, routed through prepared_execution_session_runner`

The benchmark pressure app is Barnes-Hut, but the frozen runtime family is not
Barnes-Hut-specific. The productized runtime primitive is:

- `src/rtdsl/prepared_execution.py`
- `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`

Here "generic" means the runtime API is app-name-free and accepts compatible
aggregate-tree/vector inputs; it does not mean this family has already been
validated across multiple pressure apps.

The current pressure-route adapter is:

- `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- mode `prepared_execution_fused_vector_sum_numba_cuda`

The control mode is:

- `fused_frontier_force_sum_bucketized_numba_cuda`

The historical no-go/reference mode is:

- `prepared_aggregate_frontier_weighted_vector_optix`

This is the right first Set-A family because it is multi-phase,
residency-sensitive, continuation-aware, and already has a productized runner
path that can be judged without an all-app rerun.

## Non-Decision

This freeze authorizes no Phoenix V3 release, no all-app run, no broad
V3-over-V2 wording, no public speedup wording, no RT-core speedup wording, no
true-zero-copy wording, no automatic partner selection, and no V4/embedding
scope.

## Why This Family First

RTDBSCAN and RayJoin remain important Set-A candidates, but their current
productized-runner evidence is not material:

- RTDBSCAN M3.1 runner-vs-legacy was a severe loss.
- RTDBSCAN M3.4 recovered only to parity, about `0.9976x`.
- RayJoin has structural runner evidence but not a material runtime-sourced
  win.

Barnes-Hut aggregate-tree fused vector accumulation is different: a fixed POD
A/B already shows that the productized runner preserves the existing high-speed
fused Numba CUDA route at parity while retaining the internal residency and
metadata gates.

## Existing Evidence

Focused POD evidence:

`docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718/`

Report:

`docs/reports/phoenix_v3_step1_barnes_hut_runner_parity_pod_ab_2026-06-22.md`

External review:

`docs/reviews/second_ai_phoenix_v3_barnes_hut_runner_fixed_review_2026-06-22.md`

POD hardware:

- `NVIDIA RTX 4000 Ada Generation`
- driver `550.127.05`

Provenance caveat: the prior evidence packet records local base commit
`8e0f052bffec02507aaf5ed05f75dfe995f39883`, but the remote execution tree
`/root/rtdl_v3_rebuild_20260620/current` was not a git checkout and therefore
its evidence `summary.json` records `git_commit: null`. M29 must restate this
instead of inventing a remote commit.

Protocol already used:

- body counts: `32768`, `65536`, `131072`
- `theta=0.5`
- `bucket_size=32`
- `max_depth=32`
- `query_repeat=11`
- `warmup=3`
- `samples=5`

Observed current-runner parity against current fused control:

| Bodies | Runner hot median (s) | Current fused-control hot median (s) | Runner/control |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.010791808 | 0.010797493 | 1.000527x |
| 65,536 | 0.015773401 | 0.015763111 | 0.999348x |
| 131,072 | 0.041481458 | 0.041403107 | 0.998111x |

Geomean runner/control: `0.999328x`.

The evidence `summary.json` field `runtime_sourced_material_gain: true` is
keyed to the historical prepared-OptiX-frontier reference displacement below,
not to current runner versus current fused control. Current runner versus
current fused control is parity evidence, not material-gain evidence.

Historical prepared-OptiX-frontier reference over current runner:

| Bodies | Historical OptiX hot median (s) | Runner hot median (s) | Historical/runner |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.094951779 | 0.010791808 | 8.798505x |
| 65,536 | 0.214636602 | 0.015773401 | 13.607503x |
| 131,072 | 0.714862727 | 0.041481458 | 17.233308x |

Geomean historical/runner: `12.730691x`.

This historical leg is a no-go route displacement reference, not the primary
public performance claim.

All 45 row payloads set `validation_skipped: true` with reason
`user_skip_validation` because the serious large rows skip per-row CPU/oracle
validation to avoid changing the performance run into an oracle run. Correctness
for this freeze is therefore carried by the summary-level runner/control
equivalence gate: contribution count plus checksum X/Y match at every serious
size.

## V2.14 / Current Comparison Rule

M28 freezes the comparison rule; it does not yet authorize a final V2.14/current
claim.

Fresh M29 evidence must inspect the `v2.14` tag on the same RT-hardware pod and
classify the available Barnes-Hut surface before timing. Local tag inspection
already shows:

- `v2.14` contains a Barnes-Hut research benchmark.
- `v2.14` contains CPU-side fused force-summary and grouped-vector typed-stream
  descriptor routes, including `fused_frontier_force_sum_bucketized_cpu` and
  `grouped_vector_sum_typed_stream_plan`.
- `v2.14` does not contain the current mode names
  `fused_frontier_force_sum_bucketized_numba_cuda`,
  `prepared_execution_fused_vector_sum_numba_cuda`, or
  `prepared_aggregate_frontier_weighted_vector_optix`.
- `v2.14` does not contain
  `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`.
- `v2.14` Barnes-Hut release evidence centers on prepared fixed-depth
  node-coverage, including a 1,000,000 bodies x 65,536 nodes hot-query row where
  OptiX was about `2.06x` faster than Embree.

Therefore M29 must not pretend that the current fused force-vector continuation
has a direct same-mode V2.14 baseline unless the fresh checkout proves one.

Accepted M29 classifications:

1. `v2_14_lacks_current_trunk_surface`
   - V2.14 lacks the current productized runner and fused force-vector
     continuation surface.
   - Allowed claim: Phoenix V3 adds/productizes a runtime-trunk family that
     V2.14 did not expose.
   - Not allowed claim: same-contract V3 speedup over V2.14 for this exact
     current mode.

2. `v2_14_has_equivalent_fused_surface`
   - If a fresh v2.14 checkout exposes an equivalent fused route under another
     name, M29 must compare current runner against that route.
   - Required floor: every serious row `>=0.95x`, geomean `>=0.98x`.
   - Interpretation: productized runner preserves speed; it is not a material
     speed win unless the ratio also clears `>=1.15x`.

3. `v2_14_has_cpu_fused_or_typed_stream_only`
   - Compare only as a contract-bound CPU/typed-stream reference.
   - Required wording: V2.14 had useful force-vector/generic-stream pieces, but
     not the current productized Numba CUDA runner route.

4. `v2_14_has_only_node_coverage_or_frontier_route`
   - Compare only as a contract-bound reference.
   - Required wording: different contract, useful release-era reference, not a
     public same-contract speedup.

## Set-A Credit Gates

The family may count as one Phoenix V3 Set-A runtime-trunk probe only if all
of these are true:

- `prepared_execution_session_runner_used=True` for every runner sample.
- `productized_execution_path=prepared_execution_session_runner` or equivalent
  runner metadata is present.
- `runtime_trunk_executes_end_to_end=True` for every runner sample.
- `internal_device_residency_between_rtdl_phases=True` for every runner sample.
- `frontier_rows_materialized_on_host=False`.
- `contribution_rows_materialized_on_host=False`.
- `hot_path_host_materialization=False`.
- output contract matches the requested
  `generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1`.
- partner is explicit `numba_cuda`; no automatic partner selection.
- runner/control output equivalence passes by contribution count and force
  checksum X/Y at every serious size.
- current runner vs current fused control passes every size `>=0.95x` and
  geomean `>=0.98x`.
- if an equivalent V2.14 fused route exists, current runner vs V2.14 equivalent
  route must also pass every size `>=0.95x` and geomean `>=0.98x`.
- any material speed classification must clear at least `>=1.15x` geomean;
  `>=1.20x` remains the preferred release-quality bar.

## Stop Conditions

Stop and do not count this family as Set-A if any of these occurs:

- runner metadata is absent or weak;
- residency metadata is false;
- hot-path host materialization appears;
- current runner is below `0.95x` on any serious size against current fused
  control;
- current runner/control geomean is below `0.98x`;
- output equivalence fails;
- the report tries to use the historical OptiX/frontier leg as the primary
  public claim;
- the report implies RT-core speedup for the Numba CUDA fused route;
- the report treats V2.14 node-coverage and current fused force-vector
  continuation as the same contract;
- all-app timing is started before this family and one more true Set-A family
  are accepted.

## Next Work And POD Cost

M28 is a documentation and external-review freeze; it needs no POD.

M29 should run the fresh v2.14/current Barnes-Hut classification on the user's
existing POD:

- expected wall time: 1-2 working hours;
- expected POD time: 0.5-1.5 hours;
- approximate cost at `$1 / 4 hours`: `$0.13-$0.38`.

If M29 confirms this as one accepted Set-A family, M30 should pick the second
Set-A family, likely RTDBSCAN/resident component continuation or an RTNN-style
resident graph/partner continuation path:

- expected wall time: 4-8 working hours for a focused probe;
- expected POD time: 2-6 hours;
- approximate cost: `$0.50-$1.50`.

Only after two Set-A probes are accepted should a serious all-app V2.14/current
run be planned:

- expected POD time: 4-8 hours for one disciplined pass;
- approximate cost: `$1.00-$2.00`.

## Goal-Level Decision Audit

Decision: freeze Barnes-Hut aggregate-tree fused weighted-vector sum as the
first Set-A runtime-trunk family, but require M29 to separate productized-trunk
evidence from any V2.14/current speed claim.

1. Was I foolish?
   No for this decision. It follows the reviewed redirect: trunk first, all-app
   later.

2. If yes, what actions made the decision foolish?
   The foolish action would be to count the `12.73x` historical OptiX/frontier
   displacement as a public V3-over-V2 claim or to hide that current fused
   control is already fast. This document explicitly blocks that.

3. Was there another path that avoided being stuck?
   Yes. Continue RTDBSCAN or RayJoin first. That path is still possible, but the
   existing evidence says those routes currently have structural runner evidence
   without material gain.

4. Can I now try a different path that truly solves the problem?
   Yes. Use this family as the first focused trunk proof, then require one more
   true Set-A family before all-app timing.

## Non-Authorization

This file authorizes no release, no broad V3-over-V2 wording, no public speedup
wording, no RT-core speedup wording, no true-zero-copy wording, no V4 work, and
no all-app POD run.
