# Goal2638 3-AI Consensus

Date: 2026-05-27

Participants:

- Codex: implementation and response owner.
- Gemini 3.1 Pro: first external review.
- Claude: second external review after first remediation pass.

Related artifacts:

- `docs/reports/goal2638_aggregate_frontier_collect_2026-05-27.md`
- `docs/reports/goal2638_claude_critical_review_2026-05-27.md`
- `docs/reports/goal2638_external_review_response_2026-05-27.md`
- `docs/reports/goal2639_aggregate_frontier_native_abi_contract_2026-05-27.md`

## Consensus Decision

`AGGREGATE_FRONTIER_COLLECT_2D` is accepted as a candidate RTDL primitive
contract for app-independent aggregate-frontier row collection.

The accepted scope is deliberately narrow:

- CPU reference implementation;
- row-major i64 frontier rows;
- source IDs plus row offsets;
- fail-closed exact capacity checks;
- reserved `metadata_flags` lane;
- columnar and Torch/CuPy partner-column adapters;
- Barnes-Hut benchmark mode that exercises the generic contract without
  embedding force math.

This is not a native Embree/OptiX promotion and not an RT-core performance
claim.

## Boundary Consensus

All three reviewers agree on the core boundary:

- The engine may own aggregate-tree traversal and frontier ID collection.
- The engine may own generic row schemas, capacity semantics, and backend
  lowering plans.
- The engine must not own Barnes-Hut inverse-square force law, mass-weighted
  scoring, timestep integration, or app-specific reductions.
- Distance/opening-ratio values are diagnostics only and are not part of
  default primitive rows.
- Native Embree/OptiX lowering remains future work.

## Review-Driven Changes Accepted

- `metadata_flags` is now part of the row schema with explicit current
  semantics: `0` means no flags set.
- Partners must ignore unknown future non-zero flags unless a later contract
  revision documents them.
- `distance` and `opening_ratio` are removed from default `frontier_rows`.
- Optional debug fields are exposed only through
  `include_debug_diagnostics=True`.
- Overflow messages use "attempted" rather than "emitted" because failed rows
  are abandoned before materialization.
- Barnes-Hut inverse-square force helpers are moved from
  `src/rtdsl/aggregate_tree_reference.py` to
  `src/rtdsl/app_reference/aggregate_force_math.py`.
- Existing top-level `rtdsl.*` names remain as compatibility exports, but the
  implementation source is now app-reference code.
- Primitive hierarchy output fields now match the aggregate-frontier row
  schema plus `row_offsets`.
- Partner adapter metadata now uses `partner_i64_row_layout_ready`, avoiding a
  false device-residency implication.

## Verification Consensus

The following local checks were run after remediation:

```bash
PYTHONPATH=src:. python3 - <<'PY'
import rtdsl as rt
print(rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA)
print(rt.AGGREGATE_FRONTIER_COLLECT_ROW_METADATA_FLAGS_NONE)
print(rt.WEIGHTED_INVERSE_SQUARE_VECTOR_SUM_2D_CONTRACT)
print(rt.sum_weighted_inverse_square_contributions_2d.__module__)
PY

PYTHONPATH=src:. python3 -m unittest tests.goal2638_aggregate_frontier_collect_test

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2538_barnes_hut_fused_frontier_vector_sum_test \
  tests.goal2549_native_engine_boundary_rejection_test \
  tests.goal2624_primitive_hierarchy_test

PYTHONPATH=src:. python3 -m unittest \
  tests.goal2531_barnes_hut_generic_opening_rows_test \
  tests.goal2532_barnes_hut_benchmark_app_completion_test \
  tests.goal2533_barnes_hut_generic_force_contributions_test \
  tests.goal2534_barnes_hut_streamed_vector_sum_test \
  tests.goal2535_barnes_hut_materialization_pressure_test \
  tests.goal2539_barnes_hut_same_contract_cpp_baseline_test \
  tests.goal2540_barnes_hut_benchmark_app_closeout_test \
  tests.goal1979_exact_pairwise_force_partner_barnes_hut_reference_test

git diff --check
```

Observed result: all listed tests passed, and `git diff --check` reported no
whitespace errors.

## Non-Claims

This consensus does not authorize:

- native Embree aggregate-frontier execution claims;
- native OptiX aggregate-frontier execution claims;
- RT-core speedup claims;
- RT-BarnesHut paper reproduction claims;
- whole-app Barnes-Hut performance claims;
- any claim that the RTDL engine computes Barnes-Hut force.

## Next Required Work Before Promotion

Promotion beyond candidate behavior requires a native evidence cycle. The
app-name-free native ABI contract and local Embree native row collector are now
specified in Goal2639, but OptiX implementation and cross-backend evidence
remain pending:

1. Validate Embree against the CPU reference contract on configured hosts.
2. Implement app-name-free OptiX aggregate-frontier collect.
3. Validate both against the CPU reference contract.
4. Record same-contract timing on a CUDA/OptiX pod.
5. Run external review again before promotion or public performance wording.
