---
date: 2026-04-10
goal: 198
reviewer: Claude Sonnet 4.6
subject: Fixed-Radius Neighbors Truth Path
---

## Verdict

Goal 198 is correctly scoped and honestly implemented. The Python truth path works, the semantics are right, and the baseline wiring is coherent. One gap exists in the CLI scaffolding that does not affect any tested path but would cause a misleading failure if `baseline_runner.py main()` were invoked for this workload directly from the command line.

## Findings

**Scope discipline — clean.** `run_cpu_python_reference` dispatches `fixed_radius_neighbors` to `fixed_radius_neighbors_cpu` and nothing else (`runtime.py:138–144`). The `run_cpu` / `run_oracle` branch has no case for the predicate and would correctly raise on any attempt to reach it. `baseline_contracts.py` notes explicitly state Python-reference only; no `cpu`, `embree`, `optix`, or `vulkan` closure is advertised.

**Inclusive-radius semantics — correct.** The filter `if distance_sq > radius_sq: continue` (`reference.py:187`) admits points where `distance == radius` (squared comparison, inclusive boundary). The stored distance is then `math.sqrt(distance_sq)`, so the emitted value is the true Euclidean distance, not the squared one. No issue.

**Ordering and truncation — correct.** `candidates.sort(key=lambda item: (item[0], item[1]))` sorts ascending distance first, then ascending `neighbor_id` — matching the documented contract. `candidates[:k_max]` truncates after sorting, not before. The authored test case exercises both the tie-break path (query 100, neighbors 2 and 3 at equal distance 0.3 broken by id) and the `k_max` truncation path, and the assertions are tight.

**Baseline wiring — coherent with one CLI gap.** `baseline_contracts.py` lists three representative datasets for `fixed_radius_neighbors`; `_load_fixed_radius_neighbors_case` in `baseline_runner.py` handles all three by name with no uncovered branch. The public fixture loader reads from a local path, not a live network URL. The gap: `baseline_runner.py:main()` (lines 559–573) has no `elif args.workload == "fixed_radius_neighbors"` branch and falls through to `point_nearest_segment_reference`. Invoking `python -m rtdsl.baseline_runner fixed_radius_neighbors` from the CLI would load the wrong kernel and fail at contract validation — a confusing error. All tests invoke `run_baseline_case` directly and are unaffected.

**Minor — absolute path in test.** `test_natural_earth_loader_and_case` (`goal198_fixed_radius_neighbors_truth_path_test.py:52`) hardcodes `/Users/rl2025/rtdl_python_only/tests/fixtures/...` while the example helper correctly uses `ROOT`-relative resolution. Not a correctness defect, but not portable.

**Loader eagerly imports embree_runtime.** `load_natural_earth_populated_places_geojson` calls `pack_points` from `embree_runtime` before returning (`datasets.py:505–507`). This matches the pre-existing pattern in `chains_to_probe_points` and `chains_to_polygons` and does not affect the Python truth path (inputs are cast to plain `tuple` before entering `run_cpu_python_reference`). Not a Goal 198 regression.

## Summary

The semantics — inclusive radius, distance-then-id sort, post-sort truncation — are implemented exactly as specified and exercised by tight authored assertions. The truth path is genuinely Python-only; no native or oracle dispatch was introduced. The baseline contract is honest and the dataset wiring is complete for all tested surfaces. The only actionable item is adding a `fixed_radius_neighbors` branch to `baseline_runner.py:main()` so the CLI entry point does not silently load the wrong kernel.
