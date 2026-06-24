# Goal4013 Claude Review: Goal4012 Partition-Convergence Contract Hardening

Date: 2026-06-08
Reviewer: Claude (external review, read-only)
Scope: `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py`,
`src/rtdsl/__init__.py`,
`docs/reports/goal4012_partition_convergence_contract_after_factor_sweep_2026-06-08.md`,
`tests/goal4012_partition_convergence_contract_after_factor_sweep_test.py`,
`docs/research/future_version_to_do_list.md`,
and the cited Goal4007/Goal4009/Goal4011/Goal4005 evidence reports and tests.

## Verdict

`accept`

## Summary

Goal4012 is a pure contract/metadata hardening step: it extends the
`partition_convergence_hybrid` candidate's evidence-goal tuple, requirements
tuple, and adds a new `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE`
constant that encodes the Goal4011 partition-factor result and the Goal4009
root-mutation rejection as machine-readable, app-agnostic guidance for the next
native slice. No runtime behavior changes — `grouped_stream` remains the only
supported strategy, `partition_convergence_hybrid` still returns
`candidate_requires_native_implementation`, and every release/performance/
dispatch/partner-selection/app-specific-engine flag stays `False`. I could not
execute the cited test suite in this session (Python execution required
approval that the harness did not grant), so the verdict rests on static
inspection of the source diff, the new test file, the evidence reports, and
cross-referencing against the Goal4005 contract test that the extended tuples
must remain compatible with — not on a fresh test run.

## Findings

### Q1 — Does it correctly incorporate Goal4007/4009/4011 evidence?

Yes. `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_EVIDENCE_GOALS` extends the prior
`("Goal3999", "Goal4001", "Goal4002", "Goal4004")` tuple by appending `Goal4007`,
`Goal4009`, `Goal4011` (lines 51-59) — it is additive, not a replacement, so the
Goal4005 contract test's `assertIn("Goal3999", ...)` still holds. The new
`recommended_tested_cell_factor: "radius_x_0.125"` in the partition guidance
(line 61) matches the Goal4011 report's "Best factor" column for all three
profiles (`clustered3d`, `road3d`, `ngsim_dense`, all `radius_x_0.125`). The
`required_status_counters` list folds in `root_find_invocations` and
`root_find_parent_link_steps` (lines 77-78), which are exactly the two new
counters Goal4007 added to the telemetry ABI
(`uint64[8]=root_find_invocations`, `uint64[9]=root_find_parent_link_steps`).
The `default_root_policy: "readonly_root_find_until_explicit_convergence_policy_exists"`
(line 82) is a faithful restatement of Goal4009's conclusion ("the next viable
route remains the Goal4005 partition-convergence hybrid, with an explicit
deterministic component-root policy"). Nothing in the new constants
overstates or understates what those three reports actually found.

### Q2 — Does it reject dense matrices and hidden root halving while preserving the accepted route?

Yes, and consistently across three layers (requirements tuple, guidance dict,
and rejected-shortcuts list — not just one place that could drift):

- `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS` adds
  `no_dense_cell_pair_matrix`, `compressed_occupied_partition_key_structure`,
  `bounded_near_partition_enumeration`, `readonly_root_find_default_preserved`,
  `explicit_root_convergence_changes_only`, `root_read_telemetry_reduction_required`,
  and `radius_x_0_125_partition_factor_evidence` (lines 36-48).
- The guidance dict's `dense_cell_pair_matrix_allowed: False` and
  `required_partition_pair_enumeration:
  "compressed_occupied_partition_keys_with_bounded_near_offsets"` (lines 62-65)
  directly encode the Goal4011 finding that occupied-cell pair counts at
  `radius_x_0.125` (139M/162M/1.8B theoretical pairs) make a dense matrix
  infeasible.
- `rejected_shortcuts` explicitly names both
  `dense_all_cell_pair_matrix` and
  `hidden_root_path_halving_inside_readonly_find` (lines 84-85), which is a
  direct, traceable encoding of the Goal4009 rejection rationale ("Do not
  replace `find_grouped_union_root_readonly` with a mutating helper").
- `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_SUPPORTED_STRATEGIES` is untouched
  (`("grouped_stream",)`, line 27); `partition_convergence_hybrid` remains in
  `CANDIDATE_STRATEGIES` only (lines 28-30), and
  `plan_v2_8_fixed_radius_graph_component_continuation` still routes that
  strategy through the `candidate_requires_native_implementation` branch
  (lines 316-346) rather than `accepted_preview`. The accepted grouped-stream
  route and its `V28FixedRadiusGraphComponentPlan` path (lines 347-360) are
  byte-for-byte unchanged by this diff.

### Q3 — Are claim boundaries kept fail-closed?

Yes. The diff does not touch `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_CLAIM_BOUNDARY`
(lines 89-96, unchanged) or any of the boolean authorization flags in
`V28FixedRadiusGraphComponentPlan` (lines 111-119) or the
`candidate_requires_native_implementation` branch (lines 326-336):
`runtime_executable`, `native_abi_added`, `fallback_selected`,
`hidden_dispatch_allowed`, `automatic_partner_selection_allowed`,
`app_specific_engine_logic_allowed`, `release_authorized`,
`public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
`whole_app_speedup_claim_authorized`, and `true_zero_copy_claim_authorized`
all remain hard-coded `False`. The new `app_specific_dbscan_or_clustering_native_abi`
entry in `rejected_shortcuts` (line 86) is an extra fail-closed statement, not
a relaxation — it explicitly forecloses the temptation to let the next native
slice grow DBSCAN-shaped vocabulary, consistent with Goal4007's "the next
performance primitive should not be an app-shaped DBSCAN ABI" framing and the
`future_version_to_do_list.md` "Engine boundary" note (lines 180-183) that the
native vocabulary must stay generic. The companion report
(`goal4012_partition_convergence_contract_after_factor_sweep_2026-06-08.md`)
states plainly that the change "does not add a native ABI... does not change
the accepted grouped-stream runtime route, and does not authorize public
speedup wording," and does not overclaim runtime readiness anywhere I could
find — every "next step" sentence is phrased as a requirement for the *future*
native slice, not as a claim about present capability.

### Q4 — Are the exposed metadata fields discoverable and app-agnostic?

Yes, with one minor note. The new
`V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE` constant is
exported from both the front-door module's `__all__` (lines 603-604 in the
diff) and re-exported through `src/rtdsl/__init__.py` (new import at line 413,
new `__all__` entry at line 2250), and is reachable two ways: directly as a
module constant and nested under
`describe_v2_8_fixed_radius_graph_component_front_door()["candidate_strategy_partition_guidance"]["partition_convergence_hybrid"]`
(lines 254-256) and flatly under
`plan_v2_8_fixed_radius_graph_component_continuation(...)["candidate_strategy_partition_guidance"]`
(line 343) for the selected strategy — this nested-vs-flat split mirrors the
existing `candidate_strategy_requirements`/`candidate_strategy_evidence_goals`
pattern (lines 248-253 vs. 341-342), so it is consistent with established
convention rather than a new inconsistency. The vocabulary in
`required_device_resident_columns` (`point_partition_ids`,
`occupied_partition_keys`, `partition_offsets`, `partition_counts`,
`partition_aabbs`) and `required_status_counters` stays generic — partitions,
groups, component roots, convergence, status counters — with no DBSCAN,
clustering, epsilon, min-points, or app-specific labels, matching the
`future_version_to_do_list.md` engine-boundary guidance.

Minor note (not a blocker): `V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE`
is a plain mutable `dict` exported as a module-level "contract" constant,
unlike most of the surrounding contract data in this file, which uses
immutable tuples (`HYBRID_REQUIREMENTS`, `HYBRID_EVIDENCE_GOALS`,
`CLAIM_BOUNDARY`, etc.). A caller could in principle mutate the shared dict
in place and have that mutation observed through every other accessor
(`describe_...()`, `plan_...()`, the module constant itself) since none of
them copy it. This mirrors a pre-existing pattern elsewhere in the codebase
(e.g. `v2_8_typed_result_stream.py`, `v2_8_segmented_typed_stream_adapter.py`
also export plain dict constants), so it is not a regression Goal4012
introduced, but it is the first such mutable-dict contract constant in *this*
file and worth keeping in mind if a future goal needs to harden against
accidental in-place mutation of shared contract metadata.

### Test coverage

`tests/goal4012_partition_convergence_contract_after_factor_sweep_test.py`
checks all the load-bearing claims: evidence-goal membership, the seven new/
existing requirement strings, the partition-guidance shape (recommended
factor, dense-matrix flag, enumeration strategy, required columns, rejected
shortcuts), the candidate plan's non-executable/non-authorizing flags, and
that both the source and the report contain the key claim-boundary phrases
(`test_report_and_source_record_goal4012_boundary`, lines 84-96). I traced
each assertion back to the corresponding source line and report sentence by
hand and found no mismatch. I was not able to execute
`py -3 -m unittest tests.goal4012_... tests.goal4005_... tests.goal4011_...
tests.goal4009_... tests.goal4007_...` in this session — the harness withheld
approval to run Python — so I cannot independently confirm green test output;
this is a gap in my validation, not a finding against Goal4012 itself, and the
static trace gives me high confidence the suite passes as written.

## Boundary Statement Check

Confirmed unchanged and present: no release, no public/RT-core/whole-app/
true-zero-copy/automatic-partner/hidden-dispatch/app-specific-engine claim is
authorized anywhere in the diff, the new constants, or the companion report.
`grouped_stream` remains the sole supported (executable) strategy;
`partition_convergence_hybrid` remains fail-closed pending a native
implementation that passes same-contract parity on dense and sparse pod
profiles, exactly as the report's closing paragraph states.
