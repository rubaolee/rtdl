# Goal4047 RT-DBSCAN Partition Signature App Mode

Date: 2026-06-08

## Purpose

Goal4047 exposes the Goal4045/4046 partition-convergence component-size
signature path through the RT-DBSCAN benchmark app as an explicit candidate
mode:

`partner_cupy_partition_convergence_component_signature_3d`

This is a benchmark-surface cleanup step, not a default-route promotion. The
new mode lets users run the narrow generic output contract that Goal4046 showed
was faster than full component-label materialization when the consumer only
needs sorted component sizes.

## What Changed

The RT-DBSCAN benchmark app now has a no-row mode that:

- calls
  `build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d`;
- returns `signature.contract =
  fixed_radius_graph_component_size_signature_3d`;
- rejects `--include-rows`, because the mode deliberately avoids Python row
  materialization;
- validates against the matching fixed-radius graph component reference, not
  against the CPU DBSCAN core/border/noise oracle;
- records `partition_convergence_hybrid_candidate: True` and
  `partition_convergence_hybrid_promoted: False`;
- records `full_dbscan_semantics: False` and
  `graph_component_contract_only: True`.

The app README now lists the mode beside the other RT-DBSCAN research
benchmark modes.

## Pod Validation

After committing the app mode, the pod was synced from `origin/main`:

`b7db6406`

The CUDA/CuPy smoke artifact is:

- `docs/reports/goal4047_rt_dbscan_partition_signature_app_mode_pod_smoke.json`

The smoke ran:

```bash
PYTHONPATH=$PYDEPS124:src:. python3 examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py --mode partner_cupy_partition_convergence_component_signature_3d --dataset tiny
```

The artifact records:

- `matches_reference: true`;
- `signature.contract: fixed_radius_graph_component_size_signature_3d`;
- `claim_boundary.full_dbscan: false`;
- `claim_boundary.rt_core_accelerated: false`;
- `metadata.partition_convergence_hybrid_promoted: false`;
- `metadata.graph_component_contract_only: true`.

A focused pod test gate also ran 16 tests across Goals 4043-4047 and passed.

## Why This Matters

Goal4046 proved a language/runtime lesson: expose the smallest generic output
contract that the user actually needs. A component-size signature can be useful
for benchmark scoring, convergence checks, and topology summaries without
forcing the runtime to copy or compact one label per point.

Putting this mode in the app makes that lesson executable by a learner. Keeping
it outside the default route protects the larger RT-DBSCAN claim boundary,
because this partition path is currently a pure CuPy preview and does not use
OptiX RT traversal.

## Boundary

This goal does not promote `partition_convergence_hybrid`, does not claim full
DBSCAN semantics, does not claim RT-core acceleration, does not authorize public
speedup wording, does not authorize release action, does not authorize hidden
dispatch or automatic partner selection, and does not add any native DBSCAN ABI
or app-specific engine logic.
