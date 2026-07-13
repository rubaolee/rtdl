# RT-BarnesHut Review Opinions Register

Date: 2026-07-06

## Purpose

This register makes the review trail for the RT-BarnesHut reorganization explicit. It records every material review opinion currently governing the line, its source file, whether the required action was completed, and what carry-forward constraints remain.

The intent is to prevent review feedback from living only in chat or being scattered across individual goal files.

## Current Review State

```text
Goals5063-5074: approved as generic aggregate-hierarchy rearchitecture
Goal5075: approved
Goal5076: superseded for closeout by reviewed Goal5079 live POD evidence
Goal5077: reviewed and approved
Goal5078: superseded for closeout by reviewed Goal5079 live POD evidence
Goal5079: reviewed; required amendments completed
Goal5080: reviewed; required amendments completed
Goal5081: reviewed and approved
Goal5082: reviewed and approved
Goal5083: reviewed and approved; bounded same-input line closed
Goal5084: reviewed and approved; intermediate debt disposed
```

## Review Records

### 1. Goal5065 Design Review

Source:

- `history/internal_docs/review_goal5065_rt_barneshut_hierarchy_traversal_api_design_2026-07-06.md`

Verdict:

```text
approve_with_required_amendments
```

Material opinions:

- The aggregate hierarchy direction is valid, but public API names must not contain app identity.
- `BarnesHutOpening` was not acceptable as a generic public symbol.
- Bounded same-input reproduction must not be represented as full paper reproduction.
- The narrow RTDL force-kernel ratio must always carry whole-envelope timing context.
- Genericity needs a substantially different reducer/opening proof, not another near-identical inverse-square route.
- Regression gates must be quantified.

Resolution:

- Fixed in `history/internal_docs/goal5065_review_amendment_response_2026-07-06.md`.
- Independently recorded as verified in `history/internal_docs/review_goal5065_amendments_verified_signoff_2026-07-06.md`.

Carry-forward constraints:

- Public generic APIs must remain app-name-free.
- Narrow kernel timing can be mentioned only with the broader unfavorable whole-envelope context.
- Contract/schema authorization does not authorize backend rewrite or author comparator promotion.

### 2. Goal5065 Amendment Response

Source:

- `history/internal_docs/goal5065_review_amendment_response_2026-07-06.md`

Status:

```text
all blocking findings and required amendments addressed
```

Material resolutions:

- `BarnesHutOpening` replaced by `SizeDistanceOpening(max_ratio=...)`.
- `paper_reproduction_complete` set to false where appropriate.
- `bounded_same_input_reproduction_complete` added for the narrower success state.
- RTDL narrow timing ratio paired with the broader reported envelope.
- RTDL mean ratio recorded.
- Goal5070 made non-isomorphic by requiring a substantially different reducer/opening.
- Goal5069 gate quantified as `resident_kernel_mean <= 1.37 ms`.

Carry-forward constraints:

- Goal5066 and later core work must stay generic.
- Any app-owned comparator, prepared-state reader, or force-output interpretation stays under `Paper-reproduction-apps/rt-barneshut-paper/`.

### 3. Goal5065 Amendment Verification Sign-Off

Source:

- `history/internal_docs/review_goal5065_amendments_verified_signoff_2026-07-06.md`

Verdict:

```text
amendments_verified__authorize_goal5066_contract_schema_only
```

Material opinions:

- The amendments are verified, not merely asserted.
- Goal5066 is authorized only as contract/schema work.
- Backend rewrite, author comparator promotion, and paper-completion claims remain unauthorized.

Carry-forward constraints:

- Treat this as the gate that allowed the Goal5066-5074 implementation line to proceed.

### 4. Consolidated Antigravity Review For Goals5063-5074

Source:

- `history/internal_docs/antigravity_goals5063_5074_rt_barneshut_aggregate_hierarchy_consolidated_review_2026-07-06.md`

Verdict:

```text
approve_goals5063_5074_rt_barneshut_aggregate_hierarchy_rearchitecture
```

Material opinions:

- The sequence successfully transitions the codebase from an app-shaped diagnostic route into a generic RTDL aggregate hierarchy language surface.
- `src/rtdsl/aggregate_hierarchy.py` remains free of RT-BarnesHut app identity, author payload logic, Torch extension logic, native OptiX symbols, and paper comparator code.
- App-owned prepared-array readers, author comparator logic, and Patched-Author binary hooks remain isolated in `Paper-reproduction-apps/rt-barneshut-paper/`.
- `LeafOnlyOpening + aggregate_count` is sufficient as a non-force genericity proof.
- The CPU reference executor is a sound correctness oracle.
- The optional Numba executor is correctly classified as an optional CPU prototype, not a native/CUDA/backend-complete implementation.
- Performance, paper-completion, and author-parity claims are properly bounded.

Carry-forward recommendation:

- The next goal should be a bounded force-output bridge from generic aggregate rows.

Important clarification:

- The review text describes mapping generic reducer arrays back to physical 3D vector forces. The implementation investigation for Goal5075 found that the app's actual author force-output file is scalar, not vector. Goal5075 therefore implements a scalar force-output bridge and documents that correction explicitly.

### 5. Goal5075 Force-Output Bridge Call For Review

Source:

- `history/internal_docs/call_for_review_goal5075_rt_barneshut_generic_aggregate_force_output_bridge_2026-07-06.md`
- `history/internal_docs/goal5075_rt_barneshut_generic_aggregate_force_output_bridge_result_2026-07-06.md`

Review source:

- `history/internal_docs/antigravity_goal5075_rt_barneshut_generic_aggregate_force_output_bridge_review_2026-07-06.md`

Verdict:

```text
approve_goal5075_app_owned_scalar_force_output_bridge
```

Status:

```text
approved
```

Material questions sent for review:

- Did Goal5075 correctly identify the app output as scalar force rows rather than 3D vectors?
- Did it keep the `0.1` force scale in the app adapter rather than RTDL core?
- Did it use public generic RTDL aggregate-hierarchy APIs?
- Did it avoid torch extension, native OptiX hooks, and author payload shortcuts?
- Do tests prove Numba and CPU reference outputs map to identical scalar force rows?
- Are claim boundaries correct: not author binary comparator, not paper completion, not performance, not device-resident/native?

Material opinions:

- RTDL core remains generic and produces only reducer rows such as `reducer_value_0`.
- Barnes-Hut-specific force semantics, the `0.1` scale constant, and text force output remain in the app adapter.
- The expanded tests prove Numba reducer rows and CPU reference reducer rows map to identical scalar force results.
- The claim boundary correctly excludes author binary comparator, paper reproduction completion, performance, and native/device-resident claims.

Carry-forward constraints:

- Do not claim Goal5075 closes author binary parity.
- Do not claim full paper reproduction completion.
- Do not promote scalar force-output formatting into RTDL core.
- The next goal should be an app-owned same-input scalar force comparator gate.

### 6. Goal5076 Same-Input Scalar Force Comparator Gate

Source:

- `history/internal_docs/call_for_review_goal5076_rt_barneshut_same_input_scalar_force_comparator_gate_2026-07-06.md`
- `history/internal_docs/goal5076_rt_barneshut_same_input_scalar_force_comparator_gate_result_2026-07-06.md`

Status:

```text
superseded for bounded closeout by reviewed Goal5079 live POD generic aggregate force same-input gate
```

Material questions sent for review:

- Does the new `aggregate-numba-force-compare` CLI mode correctly compose the Goal5075 bridge with the app-owned force comparator?
- Does the shell runner consume existing patched-author same-input artifacts without moving comparator logic into RTDL core?
- Is it correct for `same_input_author_comparator` to be true for this bounded scalar force-file comparator while `paper_reproduction_complete` remains false?
- Should the next goal be POD execution against patched-author same-input prepared arrays and force dumps?

Carry-forward constraints until reviewed:

- Do not claim Goal5076 was independently reviewed unless a later review is added.
- Treat Goal5076 as historical route-validation evidence.
- Use Goal5079 live POD evidence as the same-input correctness support for closeout.

### 7. Goal5077 Same-Input Gate Runner Hardening

Source:

- `history/internal_docs/call_for_review_goal5077_rt_barneshut_same_input_gate_runner_hardening_2026-07-07.md`
- `history/internal_docs/goal5077_rt_barneshut_same_input_gate_runner_hardening_result_2026-07-07.md`

Status:

```text
reviewed and approved
```

Review source:

- `history/internal_docs/antigravity_goal5077_rt_barneshut_same_input_gate_runner_hardening_review_2026-07-07.md`

Material questions sent for review:

- Does the Python runner wrap `aggregate-numba-force-compare` without reimplementing comparison logic?
- Does it accept explicit prepared arrays and expected force files for local synthetic and POD patched-author artifacts?
- Does it fail closed on missing inputs?
- Does it avoid claiming patched-author parity when local validation uses synthetic author-contract artifacts?

Carry-forward constraints until reviewed:

- Do not claim POD patched-author parity from Goal5077 alone.
- Use Goal5077 only as runner/gate hardening.
- Actual patched-author gate execution should be a separate Goal5078.

### 8. Goal5078 Full POD Gate Generic Force Integration

Source:

- `history/internal_docs/call_for_review_goal5078_rt_barneshut_full_pod_gate_generic_force_integration_2026-07-07.md`
- `history/internal_docs/goal5078_rt_barneshut_full_pod_gate_generic_force_integration_result_2026-07-07.md`

Status:

```text
superseded for bounded closeout by reviewed Goal5079 live POD full-gate execution
```

Material questions sent for review:

- Does the full POD gate correctly include the generic aggregate force same-input gate?
- Does remote package validation include the new Python and shell gate scripts as critical entries?
- Does the result avoid claiming live POD execution or patched-author parity?
- Should the next goal be live POD execution?

Carry-forward constraints until reviewed:

- Do not claim Goal5078 was independently reviewed unless a later review is added.
- Treat Goal5078 as historical package-readiness evidence.
- Use Goal5079 live POD evidence as the full-gate execution support for closeout.
- Keep `paper_reproduction_complete = false`.

### 9. Goal5079 Live POD Generic Force Gate

Source:

- `history/internal_docs/call_for_review_goal5079_rt_barneshut_live_pod_generic_force_gate_2026-07-07.md`
- `history/internal_docs/goal5079_rt_barneshut_live_pod_generic_force_gate_result_2026-07-07.md`

Status:

```text
reviewed; approve_with_required_amendments
```

Review source:

- `history/internal_docs/review_goals5079_5080_rt_barneshut_strict_phase_and_genericity_2026-07-07.md`

Material evidence sent for review:

- Full live POD gate status is `passed_correctness_and_timing_gates__phase_boundary_review_required`.
- The eight full-gate stages passed: local contract, author source contract, POD environment preflight, author-contract RTDL CUDA gate, author comparator, generic aggregate force same-input gate, same-input author-vs-RTDL gate, and same-input performance gate.
- The generic aggregate force same-input gate used the public generic RTDL aggregate-hierarchy API and selected `continuation_payload_opening`.
- The generic aggregate force same-input gate matched the patched-author force output with `mismatch_count = 0`, `max_abs_error = 1830.0`, and `max_rel_error = 2.1112736725325853e-06`.
- The older author-policy CUDA diagnostic route also matched with `mismatch_count = 0`, `max_abs_error = 1139.0`, and `max_rel_error = 2.6233255615631954e-06`.
- The narrow resident-kernel timing ratio was `0.4112069216475026`, but the report explicitly keeps it under phase-boundary review.

Material questions sent for review:

- Is `ContinuationPayloadOpening(max_ratio=...)` a legitimate generic opening policy over continuation columns?
- Is author binary sentinel normalization correctly app-owned?
- Does the gate close bounded same-input force-output correctness without promoting full paper reproduction or whole-envelope performance claims?
- Does the environment remediation remain non-algorithmic?
- Should `paper_reproduction_complete` remain false until a separate phase-boundary and paper-scope review?

Carry-forward constraints until reviewed:

Required amendments:

- Downgrade `ContinuationPayloadOpening` from fully proven generic to app-neutral/provisional generic until a non-RT-BarnesHut consumer exists.
- State that bounded same-input correctness is same-prepared-state plus payload-matched reproduction, not independent tree construction or full paper reproduction.
- Keep the narrow resident-kernel ratio paired with the broader unfavorable envelope.

Carry-forward constraints:

- Do not claim full RT-BarnesHut paper reproduction.
- Do not claim broad performance or author-performance parity.
- Do not claim whole-envelope speedup from the narrow resident-kernel ratio.
- Keep author prepared-state parsing, comparator logic, and force-output formatting in the paper app.
- Keep `paper_reproduction_complete = false`.
- Treat `ContinuationPayloadOpening` as app-neutral but not independently genericity-proven until a non-RT-BarnesHut consumer lands.

### 10. Goal5080 Phase Boundary And Bounded Closeout

Source:

- `history/internal_docs/call_for_review_goal5080_rt_barneshut_phase_boundary_and_bounded_closeout_2026-07-07.md`
- `history/internal_docs/goal5080_rt_barneshut_phase_boundary_and_bounded_closeout_result_2026-07-07.md`

Status:

```text
reviewed; approve_with_required_amendments
```

Review source:

- `history/internal_docs/review_goals5079_5080_rt_barneshut_strict_phase_and_genericity_2026-07-07.md`

Material evidence sent for review:

- Bounded same-input scalar force correctness is closed by the generic aggregate route and legacy diagnostic route, both with `mismatch_count = 0`.
- The narrow timing phase compares author `rt_core_force = 2.083 ms` to RTDL `resident_kernel_min = 0.856544017791748 ms`, ratio `0.4112069216475026`.
- The broader reported envelope is not favorable to RTDL: RTDL compile plus tree prepare plus host-to-device plus resident kernel is `469.34572154283524 ms`, while author preprocessing plus execution is `185.44600000000003 ms`, ratio `2.530902373428573`.
- A draft `phase_boundary_review.json` was generated against the Goal5079 timing artifact, but the phase boundary gate remains blocked because no external reviewer has accepted it.

Material questions sent for review:

- Is bounded same-input correctness closed?
- Is the narrow kernel phase comparison labeled narrowly enough?
- Is the broader envelope calculation correct and sufficiently prominent?
- Should the phase review gate remain incomplete until external review?
- What wording should be allowed for future summaries?

Carry-forward constraints until reviewed:

Required amendments:

- Do not call the narrow resident force-kernel comparison an accepted performance result while the phase-boundary review gate remains blocked.
- Disclose that the narrow ratio uses RTDL `resident_kernel_min` against a single author `rt_core_force` value; prefer mean-to-mean if author repeats become available.
- Pair any narrow-kernel statement with the broader-envelope result showing RTDL about `2.53x` slower.
- Downgrade `ContinuationPayloadOpening` genericity wording as described under Goal5079.

Carry-forward constraints:

- Do not claim whole-envelope RTDL speedup.
- Do not claim full paper reproduction.
- Do not set `performance_review_complete=true` or `phase_boundary_accepted=true` without an accepted external phase-boundary review.
- Keep the allowed performance wording narrow and paired with the unfavorable broader envelope.

### 11. Goal5081 ContinuationPayloadOpening Genericity Amendment

Source:

- `history/internal_docs/call_for_review_goal5081_continuation_payload_genericity_amendment_2026-07-07.md`
- `history/internal_docs/goal5081_continuation_payload_genericity_amendment_result_2026-07-07.md`

Status:

```text
reviewed and approved
```

Review source:

- `history/internal_docs/review_goal5081_continuation_payload_genericity_amendment_verified_2026-07-07.md`

Material work:

- Added `tests/goal5081_continuation_payload_genericity_proof_test.py`.
- The test builds a non-RT-BarnesHut synthetic linearized cluster hierarchy.
- The test uses `ContinuationPayloadOpening(max_ratio=0.5)` with `aggregate_count`, not inverse-square force.
- The test exercises both the reference executor and optional Numba executor.
- Goal5079 and Goal5080 wording now says `ContinuationPayloadOpening` was provisional at their boundary and that Goal5081 supplies non-RT-BarnesHut proof.
- README wording now marks the narrow kernel comparison as pending explicit phase-boundary acceptance.

Verification:

```text
py -m unittest tests.goal5081_continuation_payload_genericity_proof_test
Ran 4 tests in 4.463s
OK

py -m unittest tests.goal5066_aggregate_hierarchy_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5081_continuation_payload_genericity_proof_test
Ran 16 tests in 4.146s
OK

py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test tests.goal5081_continuation_payload_genericity_proof_test
Ran 72 tests in 32.317s
OK (skipped=1)
```

Carry-forward constraints until reviewed:

Verified outcome:

- Goals5079-5080 BF-1 / RA-1 / RA-2 / RA-3 are completed.
- `ContinuationPayloadOpening` now has a non-RT-BarnesHut aggregate-count consumer proof.
- The reviewer noted a non-blocking future strengthening opportunity: add a fixture where an accepted aggregate uses `rope_index` and `next_index != rope_index`.

Carry-forward constraints:

- Do not set `performance_review_complete=true` or `phase_boundary_accepted=true`; Goal5081 is genericity/wording amendment work, not phase-boundary acceptance.
- Do not claim full paper reproduction or whole-envelope speedup.
- Any future public performance wording must keep the pending/accepted phase-boundary state explicit.

### 12. Goal5082 ContinuationPayloadOpening Rope-Branch Hardening

Source:

- `history/internal_docs/call_for_review_goal5082_continuation_payload_rope_branch_hardening_2026-07-07.md`
- `history/internal_docs/goal5082_continuation_payload_rope_branch_hardening_result_2026-07-07.md`

Status:

```text
reviewed and approved
```

Material work:

- Added `tests/goal5082_continuation_payload_rope_branch_test.py`.
- The synthetic non-paper fixture has `node_next_index[1] = 2` and `node_rope_index[1] = 3`.
- For sources `0` and `1`, node `1` is accepted as an aggregate, so the correct continuation path must follow `rope_index`.
- An alternate fixture deliberately confuses rope with next; projected rows differ.
- Reference and optional Numba executors match on the correct fixture.

Verification:

```text
py -m unittest tests.goal5082_continuation_payload_rope_branch_test
Ran 4 tests in 4.431s
OK

py -m unittest tests.goal5081_continuation_payload_genericity_proof_test tests.goal5082_continuation_payload_rope_branch_test
Ran 8 tests in 3.865s
OK

py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test tests.goal5066_aggregate_hierarchy_contract_test tests.goal5067_rt_barneshut_aggregate_hierarchy_adapter_test tests.goal5068_aggregate_hierarchy_descriptor_extension_test tests.goal5069_aggregate_frontier_reduce_execution_contract_test tests.goal5070_non_force_genericity_proof_test tests.goal5072_aggregate_frontier_reduce_cpu_reference_test tests.goal5073_aggregate_frontier_reduce_numba_parity_test tests.goal5081_continuation_payload_genericity_proof_test tests.goal5082_continuation_payload_rope_branch_test
Ran 76 tests in 30.944s
OK (skipped=1)
```

Carry-forward constraints until reviewed:

Verified outcome:

- Goal5082 closes the non-blocking rope-branch behavior coverage note left by the Goal5081 review.
- The fixture distinguishes `rope_index` from `next_index`, exercises accepted aggregate traversal, and remains non-RT-BarnesHut.
- No required amendments remain for Goal5082.

Carry-forward constraints:

- Do not treat Goal5082 as a phase-boundary or performance review.
- Do not claim native/CUDA aggregate-hierarchy backend completion.
- Keep the full paper reproduction and whole-envelope performance restrictions unchanged.

### 13. Goal5083 RT-BarnesHut Bounded Same-Input Closeout

Source:

- `history/internal_docs/call_for_review_goal5083_rt_barneshut_bounded_same_input_closeout_2026-07-07.md`
- `history/internal_docs/goal5083_rt_barneshut_bounded_same_input_closeout_2026-07-07.md`

Status:

```text
reviewed and approved
```

Review source:

- `history/internal_docs/review_goal5083_rt_barneshut_bounded_same_input_closeout_verified_2026-07-07.md`

Material work:

- Consolidates Goals5063-5082 into a bounded same-input closeout packet.
- Closes only same-input prepared-state scalar force correctness.
- Keeps full paper reproduction, independent tree construction, whole-envelope performance, and phase-boundary performance claims explicitly not closed.
- Carries forward the broader unfavorable envelope: RTDL about `2.53x` slower than the author envelope on the reported comparison.
- Records that Goal5081 and Goal5082 close the `ContinuationPayloadOpening` genericity and rope-branch behavior amendments.

Verified outcome:

- The bounded same-input RT-BarnesHut line is closed.
- Goal5076 and Goal5078 remain visible as intermediate review debt, but do not block this closeout because Goal5079 live POD evidence supplies the final same-input correctness evidence.

Carry-forward constraints:

- Do not claim full RT-BarnesHut paper reproduction.
- Do not claim author-performance parity or whole-envelope speedup.
- Do not mark phase-boundary performance as accepted.
- Keep Goal5076 and Goal5078 review debt visible unless separately reviewed or explicitly marked superseded / will-not-review.

### 14. Goal5084 RT-BarnesHut Intermediate Review Debt Disposition

Source:

- `history/internal_docs/call_for_review_goal5084_rt_barneshut_intermediate_review_debt_disposition_2026-07-07.md`
- `history/internal_docs/goal5084_rt_barneshut_intermediate_review_debt_disposition_2026-07-07.md`

Status:

```text
reviewed and approved
```

Review source:

- `history/internal_docs/review_goal5084_intermediate_review_debt_disposition_verified_2026-07-07.md`

Material work:

- Proposes marking Goal5076 as superseded for closeout by Goal5079's live POD generic aggregate force same-input gate.
- Proposes marking Goal5078 as superseded for closeout by Goal5079's live POD full-gate execution.
- Explicitly avoids claiming Goal5076 or Goal5078 were independently reviewed.
- Keeps the historical evidence visible.

Verified outcome:

- Goal5076 is superseded by reviewed Goal5079 live POD same-input evidence.
- Goal5078 is superseded by reviewed Goal5079 live POD full-gate execution.
- Neither Goal5076 nor Goal5078 is falsely marked as independently reviewed.
- No required review debt remains for the bounded same-input RT-BarnesHut line.

Carry-forward constraints:

- Do not claim full paper reproduction, phase-boundary acceptance, whole-envelope speedup, or native/backend completion.

## Open Review Debt

### Pending

None for the bounded same-input RT-BarnesHut line.

### Closed

- Goal5065 amendments: verified and closed.
- Goals5063-5074 consolidated rearchitecture review: approved.
- Goal5075 scalar force-output bridge review: approved.
- Goal5076 external review debt: superseded by reviewed Goal5079 live POD same-input evidence.
- Goal5077 external review: approved.
- Goal5078 external review debt: superseded by reviewed Goal5079 live POD full-gate execution.
- Goal5079 external review: complete; required amendments completed by Goal5081.
- Goal5080 external review: complete; required amendments completed by Goal5081.
- Goal5081 external review: complete and approved.
- Goal5082 external review: complete and approved.
- Goal5083 external review: complete and approved; bounded same-input line closed.
- Goal5084 external review: complete and approved; intermediate debt disposed.

## Standing Rules Derived From Reviews

1. RTDL core may expose generic aggregate-hierarchy contracts, descriptors, opening policies, reducers, and reference/optional Numba executors.
2. RTDL core must not expose RT-BarnesHut, Treelogy, AuthorOfficial, author payload, or paper-specific force-output semantics.
3. Paper app code may own prepared-state readers, author binary hooks, scalar force-output formatting, and comparator logic.
4. Narrow performance ratios must be paired with whole-envelope context.
5. `paper_reproduction_complete` must remain false unless a later review explicitly approves full paper reproduction completion.
6. Bounded same-input success must be labeled as bounded same-input success, not full Section-5 reproduction.
7. Optional Numba CPU parity is a prototype/backend candidate, not a native/CUDA implementation.
8. Future backend work must use the CPU reference executor as a correctness oracle.
9. Any future public API naming must pass the app-identity scan before promotion.
10. Any new force-output bridge must stay app-owned unless a separate generic output abstraction is reviewed.
11. `ContinuationPayloadOpening` was provisional at Goal5079/5080 review time; Goal5081 adds a non-RT-BarnesHut aggregate-count consumer proof and is externally approved.
12. Narrow resident-kernel timing may be discussed only as pending or accepted phase-boundary evidence, and only when paired with the broader unfavorable envelope.
13. Goal5082 implements the non-blocking strengthening test for accepted aggregate traversal with `rope_index != next_index`; external review is complete and approved.
14. Goal5083 closes the bounded same-input RT-BarnesHut line while preserving full-paper, phase-boundary, independent-tree-construction, and whole-envelope-performance restrictions; external review is complete and approved.
15. Goal5084 disposes of Goal5076 and Goal5078 as superseded intermediate review debt for bounded-closeout purposes; external review is complete and approved.

## Next Review Action

Next technical action:

```text
The bounded same-input RT-BarnesHut line is closed and has no remaining required review debt. Treat phase-boundary acceptance, independent tree construction, and native/backend work as separate optional future goals.
```
