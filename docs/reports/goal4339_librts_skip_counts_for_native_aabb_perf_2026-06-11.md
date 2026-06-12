# Goal4339: LibRTS Skip-Counts Guard For Native AABB Performance Rows

Date: 2026-06-11

Status: implemented locally; Linux native validation completed.

## Purpose

Goal4339 fixes a measurement bug in the LibRTS-style benchmark app before we use
Embree CPU as a serious comparison partner against NVIDIA OptiX/RT-core rows.

The problem was simple and expensive: `embree_aabb_index` always ran the
`O(boxes x queries) Python CPU oracle` after the native prepared AABB query. The
CLI already exposed `--skip-counts`, but the Embree and OptiX AABB modes did not
pass that choice into their native timing functions. As a result, a performance
packet could accidentally report Python oracle time instead of native query time.

## Change

`run_embree_aabb_counts(...)` and `run_optix_aabb_counts(...)` now accept:

```python
validate_reference: bool = True
```

The CLI passes:

```python
validate_reference=not args.skip_counts
```

When validation is enabled, the old behavior remains: the CPU oracle runs and
`matches_cpu_reference` is a real boolean.

When `--skip-counts` is used, the native path skips the quadratic Python oracle
and emits:

```text
matches_cpu_reference: null
cpu_reference_skipped: true
```

That makes large performance rows honest: they can be used as native hot-path
timing evidence only when a separate small correctness row already validated the
same contract.

## Boundary

This is not an app-specific native-engine change. The native primitive remains
the generic AABB index query contract. The change only fixes the benchmark/front
door measurement policy around when to run the expensive Python oracle.

This report does not authorize public speedup wording, release action, broad
RT-core wording, paper reproduction wording, automatic partner selection, or
app-specific native-engine logic.

## Validation

Local unit coverage:

- `tests.goal4339_librts_skip_counts_native_perf_guard_test`

The test monkeypatches the Embree prepared AABB path and verifies:

- `validate_reference=False` does not call `run_counts`;
- `matches_cpu_reference` is `None`;
- `cpu_reference_skipped` is `True`;
- default behavior still calls the CPU oracle and records a boolean match;
- CLI source wires `--skip-counts` into both native AABB modes.

Linux validation:

- Artifact directory:
  `docs/reports/goal4339_librts_skip_counts_local_linux/`
- Small validated row:
  `box_count=64`, `query_count=64`, `operation=all`, `repeat=2`,
  `warmup=1`, `matches_cpu_reference=true`, `cpu_reference_skipped=false`.
- Large skip-count row before the Goal4340 native AABB route:
  `box_count=1024`, `query_count=1024`, `operation=all`, `repeat=2`,
  `warmup=1`, `matches_cpu_reference=null`, `cpu_reference_skipped=true`,
  `query_median_sec=43.764849884002615`.

Conclusion:

- Goal4339 fixed the benchmark policy bug: large native rows can now skip the
  Python CPU oracle honestly.
- The validation also proved the deeper performance problem was not only the
  Python oracle. The pre-Goal4340 Embree AABB path still spent about 43.8s in
  native query time because it lowered AABB queries through generic columnar
  conjunctive scan rather than a real AABB index/collision primitive.
- Goal4340 therefore follows this report with a native prepared Embree
  `AABB_INDEX_QUERY_2D` route.
