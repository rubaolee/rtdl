# Goal945 Full-Suite Stabilization After Goal942

Date: 2026-04-25

## Verdict

ACCEPT locally, pending final independent peer review after the evidence-log
refresh.

Goal945 stabilizes the local test suite after the Goal941/Goal942 RTX A5000 artifact intake and public readiness promotions. The final local result is:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
Ran 1825 tests in 195.424s
OK (skipped=196)
```

Persisted log:

- `docs/reports/goal945_full_suite_unittest_2026-04-25.txt`
- `docs/reports/goal945_full_suite_unittest_verbose_2026-04-25.txt`
- `docs/reports/goal945_unittest_discovery_count_analysis_2026-04-25.txt`

## Problem

After Goal942 promoted the bounded RTX claim-review paths to `ready_for_rtx_claim_review`, the full suite exposed two classes of fallout:

1. Stale readiness, command-audit, and public-doc tests still expected the pre-Goal941 state.
2. A long-standing Embree line-segment-intersection parity miss reappeared in full-suite execution: the CPU/oracle path contained pair `(24, 368)`, while Embree missed it.

The first class was synchronization work. The second class was a real native-backend correctness bug.

## Stale-State Synchronization

The following tests and scripts were refreshed to match the current Goal941/Goal942 state:

- `tests/goal690_optix_performance_classification_test.py`
- `tests/goal691_optix_robot_summary_profiler_test.py`
- `tests/goal692_optix_app_correctness_transparency_test.py`
- `tests/goal700_fixed_radius_summary_public_doc_test.py`
- `tests/goal707_app_rt_core_redline_audit_test.py`
- `tests/goal718_embree_prepared_app_modes_test.py`
- `tests/goal761_rtx_cloud_run_all_test.py`
- `tests/goal831_segment_polygon_native_artifact_contract_test.py`
- `tests/goal838_local_baseline_collection_manifest_test.py`
- `tests/goal846_active_rtx_claim_gate_test.py`
- `tests/goal848_v1_rt_core_goal_series_test.py`
- `tests/goal858_segment_polygon_docs_optix_boundary_test.py`
- `tests/goal862_spatial_rtx_collection_packet_test.py`
- `tests/goal878_segment_polygon_native_pair_rows_app_surface_test.py`
- `scripts/goal515_public_command_truth_audit.py`
- `scripts/goal847_active_rtx_claim_review_package.py`
- `scripts/goal862_spatial_rtx_collection_packet.py`

The public command truth audit was also regenerated:

- `docs/reports/goal515_public_command_truth_audit_2026-04-17.json`
- `docs/reports/goal515_public_command_truth_audit_2026-04-17.md`

Final command-audit result:

```text
valid: true
total commands: 280
uncovered commands: 0
goal821 exact commands: 5
goal942 exact commands: 8
```

## Embree Correctness Fix

Root cause:

Embree user-geometry bounds for 2D segment primitives used exact X/Y min/max values. For near-endpoint/touching segment intersections, this allowed Embree to cull a candidate before the exact intersection callback could test it. The observed reproducer was a horizontal/near-vertical LSI case where pair `(24, 368)` was present in CPU/oracle output but absent from Embree output.

Fix:

`src/native/embree/rtdl_embree_scene.cpp` now pads segment user-geometry bounds in X and Y by `kEps`, matching the existing Z padding policy and making candidate culling conservative enough for exact callback refinement.

Verification reproducer after forced native rebuild:

```text
RTDL_FORCE_EMBREE_REBUILD=1 PYTHONPATH=src:. python3 <minimal LSI reproducer>
({'left_id': 24, 'right_id': 368, ...}, ...)
```

Focused parity verification:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal31_lsi_gap_closure_test tests.baseline_integration_test tests.evaluation_test -v
Ran 10 tests in 0.068s
OK
```

## Full-Suite Progression

Initial full-suite state after Goal942 sync work:

```text
Ran 1825 tests
FAILED (failures=28, errors=6, skipped=196)
```

After stale-state fixes but before Embree bounds fix:

```text
Ran 1825 tests
FAILED (failures=4, errors=0, skipped=196)
```

The remaining four failures were all explained by the same Embree LSI parity miss.

Final state after the Embree bounds fix, with persisted log:

```text
Ran 1825 tests in 195.424s
OK (skipped=196)
```

`git diff --check` also passed after the persisted full-suite run.

## Peer-Review Note

The first independent peer review returned `BLOCK` because the original report
relied on terminal output only and did not include a persisted full-suite log.

The second peer review still returned `BLOCK` because
`suite.countTestCases()` reports 1860 discoverable cases, while the unittest
runner summary reports 1825 executed test methods. I reproduced and explained
that mismatch in
`docs/reports/goal945_unittest_discovery_count_analysis_2026-04-25.txt`:

```text
discovered_countTestCases=1860
runner_verbose_test_method_lines=1825
missing_due_to_setUpClass_skip_or_nonexecuted=35
setUpClass_skip_events=6
```

The 35 discovered-but-not-run methods are in classes skipped from `setUpClass`
because optional OptiX/Vulkan runtimes are unavailable on this macOS checkout:

- `goal429_v0_7_rt_db_cross_engine_postgresql_correctness_gate_test`
- `goal435_v0_7_optix_native_prepared_db_dataset_test`
- `goal436_v0_7_vulkan_native_prepared_db_dataset_test`
- `goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test`
- `goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test`
- `rtdsl_vulkan_test.RtDslVulkanTest`

Therefore both numbers are true but answer different questions:
`countTestCases()` counts potential methods in discovered suites, while the
unittest runner summary reports executed test methods after class-level optional
backend skips.

## Honesty Boundary

This goal does not add new RTX performance evidence and does not authorize any new public speedup claim.

It only confirms that the current Goal941/Goal942 readiness state is internally consistent with the local test suite, and that a native Embree correctness bug in segment bounds was fixed.

## Next Required Step

Obtain independent peer review and write the Goal945 two-AI consensus before treating this stabilization as closed.
