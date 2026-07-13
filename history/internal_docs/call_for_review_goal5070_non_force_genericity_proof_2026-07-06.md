# Call For Review: Goal5070 Non-Force Genericity Proof

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5070_non_force_genericity_proof_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `src/rtdsl/__init__.py`
- `tests/goal5070_non_force_genericity_proof_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5070_non_force_genericity_proof`
- `approve_with_required_amendments`
- `block_goal5070_genericity_proof`

## Context

Goal5065 review required a future genericity proof using a substantially different reducer and opening policy. It explicitly warned that another inverse-square force-field variant is not sufficient.

Goal5070 responds by adding:

- `LeafOnlyOpening()`: topology-only opening, not size/distance;
- `aggregate_count`: non-force reducer;
- same backend-neutral execution contract from Goal5069.

## Review Questions

1. Is `LeafOnlyOpening()` substantially different from `SizeDistanceOpening(max_ratio=...)`?
2. Is `aggregate_count` substantially different from inverse-square scalar/vector reducers?
3. Does the proof avoid another inverse-square force-field variant?
4. Does the proof use the same `AggregateFrontierReduceExecutionContract3D` rather than a separate app-specific path?
5. Are unsupported opening objects rejected fail-closed?
6. Does the public API avoid RT-BarnesHut/app identity names?
7. Does the change avoid CUDA/OptiX/native backend implementation?
8. Does the change avoid paper-completion and speedup claims?
9. Did the Goal5063/5066/5067/5068/5069/5070 regression preserve the current RT-BarnesHut bounded same-input evidence?
10. Is Goal5071 release-boundary consolidation the right next step before any executor implementation?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
