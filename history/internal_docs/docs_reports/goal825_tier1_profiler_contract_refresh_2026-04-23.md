# Goal825 Tier-1 Profiler Contract Refresh

Date: 2026-04-23

## Verdict

ACCEPT. Tier-1 RTX profiler outputs now share an explicit schema marker and
machine-readable cloud claim contract.

## Updated Profilers

- `/Users/rl2025/rtdl_python_only/scripts/goal756_db_prepared_session_perf.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal757_optix_fixed_radius_prepared_perf.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal760_optix_robot_pose_flags_phase_profiler.py`

Each profiler now emits:

- `schema_version: goal825_tier1_phase_contract_v1`
- `cloud_claim_contract.claim_scope`
- `cloud_claim_contract.non_claim`
- `cloud_claim_contract.required_phase_groups`
- `cloud_claim_contract.cloud_policy`

## Claim Boundaries

- DB: prepared compact-summary sessions only; not SQL, DBMS behavior, full row
  materialization speedup, or broad RTX app speedup.
- Outlier: prepared fixed-radius threshold summary only; not KNN, Hausdorff,
  ANN, Barnes-Hut, row-output, anomaly-system, or whole-app RTX speedup.
- DBSCAN: prepared fixed-radius core-flag summary only; not full clustering or
  Python cluster expansion.
- Robot: prepared ray/triangle any-hit compact pose summary only; not full robot
  planning, kinematics, witness rows, or continuous collision detection.

## Verification

Added `/Users/rl2025/rtdl_python_only/tests/goal825_tier1_profiler_contract_test.py`
and extended existing profiler tests to assert the shared schema and claim
contract.

Focused verification passed:

- Goal825 contract tests
- Goal756 DB prepared-session profiler tests
- Goal757 prepared fixed-radius profiler tests
- Goal760 robot pose-flags profiler tests
- Goal824 pre-cloud readiness gate tests

Result: 23 tests OK, 2 skipped because prepared OptiX fixed-radius native
symbols are not available on this macOS host.

This goal is local pre-cloud work. It does not start cloud and does not
authorize speedup claims.
