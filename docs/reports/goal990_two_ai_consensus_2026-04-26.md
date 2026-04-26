# Goal990 Two-AI Consensus

Date: 2026-04-26

## Goal

Move the public Hausdorff and Barnes-Hut prepared OptiX decision paths away from count-row materialization and onto scalar prepared threshold-count continuation, while keeping witness/identity boundaries explicit.

## Codex Verdict

ACCEPT.

Codex implemented and verified:

- `examples/rtdl_hausdorff_distance_app.py` now uses `prepared.count_threshold_reached(...)` for `directed_threshold_prepared`.
- `examples/rtdl_barnes_hut_force_app.py` now uses `prepared.count_threshold_reached(...)` for `node_coverage_prepared`.
- Both public app paths report `summary_mode: scalar_threshold_count` and `row_count: None`.
- Both paths keep identity output bounded: failed scalar decisions do not invent violating source IDs or uncovered body IDs.
- The app-support matrix was refreshed with the scalar-mode boundary and no new speedup claim was authorized.

Focused verification:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal882_barnes_hut_node_coverage_optix_subpath_test \
  tests.goal887_prepared_decision_phase_profiler_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal817_cuda_through_optix_claim_gate_test

Ran 23 tests in 0.954s
OK
```

Additional checks:

```text
python3 -m py_compile \
  examples/rtdl_hausdorff_distance_app.py \
  examples/rtdl_barnes_hut_force_app.py \
  tests/goal879_hausdorff_threshold_rt_core_subpath_test.py \
  tests/goal882_barnes_hut_node_coverage_optix_subpath_test.py \
  tests/goal957_graph_hausdorff_native_continuation_metadata_test.py

git diff --check
```

Both checks passed.

## Gemini Verdict

ACCEPT.

Gemini review file:

- `docs/reports/goal990_gemini_review_2026-04-26.md`

Gemini initially accepted the app-path migration and recommended explicit failure-path tests for the scalar witness boundary. Codex added those tests, then Gemini performed a follow-up review and accepted the final state with no blockers.

## Nuance

Scalar mode does not return full witness rows. Therefore:

- If the scalar decision succeeds, the missing-identity list is empty because there are no missing witnesses.
- If the scalar decision fails, the app returns `None` for the missing-identity list and marks `identity_parity_available: False`.

This is intentional: the RT-core claim is the scalar decision path, not a witness-row extraction path.

## Consensus

Goal990 is closed with 2-AI consensus.

No public RTX speedup claim is authorized by this goal.
