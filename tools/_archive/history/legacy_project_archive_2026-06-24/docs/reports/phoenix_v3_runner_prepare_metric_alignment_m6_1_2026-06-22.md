# Phoenix V3 Runner Prepare Metric Alignment M6.1

Date: 2026-06-22
Status: `local_shared_runtime_metric_alignment_not_release`

## Why M6.1 Was Needed

Kepler accepted M6 as generic cleanup but blocked focused POD validation because
the first patch mostly affected metadata/wrapper overhead outside the known
Hausdorff M5 failed phase-total gate.

M6.1 addresses that causal gap. The Hausdorff M5 runner-vs-legacy comparison
used different prepare timing scopes:

- legacy prepared OptiX reported `prepared.scene_prepare_sec`, the native
  prepared-object timing;
- the productized runner reported `summary_sec.setup`, the outer
  cache/get/prepare/put wrapper timing.

That made the phase-total comparison partly a measurement-shape comparison
instead of a productized-trunk comparison.

## Code Changes

Changed:

- `src/rtdsl/prepared_execution.py`
- `examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`
- `scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py`
- `tests/v3_phoenix_prepared_execution_session_runner_test.py`
- `tests/v3_phoenix_hausdorff_prepared_execution_runner_wiring_test.py`

Shared runner change:

- `_execute_prepared_execution_session` now records both outer runner timing and
  native prepared-object timing when the prepared object exposes one of:
  `scene_prepare_sec`, `native_prepare_sec`, or `prepare_sec`.

New generic metadata:

```text
outer_prepare_or_cache_sec
outer_prepare_sec
outer_cache_load_sec
native_prepare_sec
native_prepare_seconds_source
legacy_aligned_prepare_sec
legacy_aligned_prepare_metric_available
```

Hausdorff canary change:

- runner route `scene_prepare_sec` now uses `legacy_aligned_prepare_sec`, which
  matches the legacy prepared OptiX phase-total scope;
- runner outer prepare/cache timing is still disclosed as
  `runner_outer_prepare_sec` and `runner_outer_cache_load_sec`;
- top-level run phases aggregate `runner_native_prepare_sec`,
  `runner_outer_prepare_sec`, and `runner_outer_cache_load_sec`.

This is not an app fast path. The generic runner supplies the timing split; the
Hausdorff canary uses it only to make the known runner-vs-legacy gate compare
the same prepare scope.

## Local Evidence

Focused gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test

36 tests OK
```

Broader runner/wording gate:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_rtdbscan_component_signature_optimization_test \
  tests.v3_phoenix_hausdorff_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_hausdorff_threshold_runner_pod_ab_test \
  tests.v3_phoenix_barnes_hut_prepared_execution_runner_wiring_test \
  tests.v3_phoenix_aabb_prepare_reuse_pod_runner_test \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_runner_overhead_microbench_test \
  tests.v3_phoenix_set_ab_scorecard_gate_test \
  tests.v3_release_wording_gate_test

56 tests OK
```

Compile:

```text
PYTHONPATH=src;. py -3 -m py_compile \
  src/rtdsl/prepared_execution.py \
  examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py \
  scripts/v3_phoenix_hausdorff_threshold_runner_pod_ab.py

OK
```

Microbench artifact:

```text
docs/rebuild/v3/evidence/phoenix_v3_runner_overhead_microbench_after_m6_1_20260622.json
```

After M6.1:

```text
noop_runner_call: 0.000730380 s/call
stable_id_read: 0.000000294 s/call
phase_to_dict: 0.000000708 s/call
report_to_dict: 0.000013586 s/call
```

## Why This Can Justify A Focused POD Canary

The change now touches the measured Hausdorff phase-total interpretation. It
does not guarantee the route will pass: rerun3 also showed a query-median gap
of about 3%. But it removes a known unfair prepare-scope mismatch and preserves
the runner outer cost for wrapper-wall checks.

Recommended canary if reviewed:

```text
Hausdorff M5 focused no-regression rerun
```

Success:

- runner-vs-legacy phase-total >= `0.98x`;
- runner-vs-legacy wrapper wall >= `0.98x`;
- runner metadata remains present;
- no threshold rows materialized on host;
- no release/public/broad/zero-copy/V4 claims.

Parity-only:

- phase-total passes but wrapper-wall remains slightly below `0.98x`;
- classify as measurement alignment plus remaining wrapper overhead, not Set-A
  material win.

Failure:

- phase-total still below `0.98x`; then the remaining issue is not just prepare
  metric scope and needs deeper primitive/query-path analysis before more POD.

## Non-Authorization

This does not authorize:

- V3 release.
- all-app pod rerun.
- public speedup wording.
- broad V3-over-V2 wording.
- whole-Hausdorff or whole-app speedup wording.
- true-zero-copy wording.
- V4 / external-buffer wording.

## Goal-Level Decision Audit

Decision: align native prepare timing and outer runner timing before asking for
focused POD validation.

1. Was I foolish?

   No for this decision. Kepler correctly pointed out that M6 did not target
   the failed phase-total gate; M6.1 fixes a measured-scope mismatch.

2. If yes, what actions made the decision foolish?

   Not applicable. The foolish action would be running POD after M6 without
   checking whether the patch could affect the failing metric.

3. Was there another path that would have avoided getting stuck?

   Yes. Inspect the phase decomposition and compare legacy-vs-runner timing
   scopes before spending POD.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is a focused Hausdorff M5 canary after fallback review,
   with native prepare and outer wrapper costs both visible.
