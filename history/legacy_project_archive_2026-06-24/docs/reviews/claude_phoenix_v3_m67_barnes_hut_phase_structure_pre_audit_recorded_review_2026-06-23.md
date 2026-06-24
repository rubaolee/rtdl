# Claude Recorded Review: Phoenix V3 M67 Barnes-Hut Phase-Structure Pre-Audit

Date: 2026-06-23
Reviewer: Claude
Status: recorded external review; non-authorizing

## Verdict

`accept_m67_count_barnes_hut_as_existing_step1_material_family_no_pod_no_release`

## Findings

### 1. Does M67 correctly reconcile M45 and M66?

Yes. The reconciliation is logically sound and does not reopen Barnes-Hut work that M45
closed.

M45 blocked new Barnes-Hut app tuning and classified the OptiX node-coverage regression as
`focused_fix_covered_pending_full_suite_validation`. It did not close the question of
whether the M28/M29 fused-runner route counts as a Step-1 material family. Those two
questions are distinct: M45 is about the frozen all-app scorecard regression; M28/M29 is
about a different route (aggregate-tree fused weighted-vector, Numba CUDA, productized
runner) that M45 explicitly separates.

M66 authorized only a local Barnes-Hut phase-structure pre-audit after the RayJoin
non-go. No POD run, no new coding branch.

M67 does exactly that: it audits existing runner-route evidence (M28/M29) to answer
whether that evidence is sufficient to count Barnes-Hut as a Step-1 material family,
then stops and asks for external review. It does not add new Barnes-Hut app tuning. The
`new_barnes_hut_app_tuning_allowed: false` and `new_barnes_hut_runtime_coding_required_now:
false` flags are correct. The verdict label `reject_m67_barnes_hut_reopened_wrong_path`
does not apply.

### 2. Is the phase-structure reading correct?

Yes. The distinction between the historical predecessor and the current fused control is
correctly drawn.

The historical prepared OptiX/frontier route (`prepared_aggregate_frontier_weighted_vector_optix`)
has a non-zero hot physical cost that the fused vector approach displaces: `12.730691x`
geomean. That route is not in v2.14 (confirmed by M29 surface matrix); it is an
intermediate V3-era route that was tried and abandoned. The 12.73x displacement is
therefore internal to V3's development history, not a v2.14 baseline comparison. This
limits its strength as a public-facing claim, but it is genuine evidence that the fused
vector approach is materially better than the old frontier approach, and it is correctly
framed as predecessor-displacement evidence only.

The current fused Numba CUDA control (`fused_frontier_force_sum_bucketized_numba_cuda`)
already removed the material frontier/contribution emission path. The runner operates after
the control already made that gain. There is no new compressible phase left for the runner
to remove, which is why `new_compressible_phase_found: false` is the correct reading.

The productized runner (`prepared_execution_fused_vector_sum_numba_cuda`) executes the
fused vector route end-to-end through the runtime trunk with internal device residency,
no host materialization of frontier or contribution rows, and output equivalence to the
current control. These three runner properties are confirmed by the checked evidence.

The phase-structure table is correct.

**Process-wall carry-forward (P2):** The phase_structure JSON records process-wall ratios
of `1.152x`, `1.181x`, and `1.159x` at the three sizes. The hot-call comparison (the
parity claim) is correct, but the runner adds 15-18% overhead at the session/process
level. This is expected session-setup cost for the productized runner and does not violate
any current check. However, this overhead must be understood before any all-app POD run
that would include process-level costs, and it must not be omitted from any future timing
characterization.

### 3. Is the parity claim valid without claiming wrapper speedup?

Yes. The claim is validly framed.

The per-size speedup ratios are `1.000527x`, `0.999348x`, and `0.998111x`. All three pass
the 0.95 per-size floor. The geomean is `0.999328x`, passing the 0.98 geomean floor.
These numbers show the runner neither beats nor meaningfully degrades the hot call. The
wording throughout M67 — and the Step-1 report itself — explicitly states this is parity
plus metadata, not evidence that the wrapper is faster. The non-authorization for
RT-core speedup claim is correctly included.

The `runner_control_output_equivalence` check is confirmed across all three sizes by
contribution count and checksum X/Y parity. There is no claim of wrapper speedup anywhere
in the M67 packet, the Step-1 report, or the M29 surface classification. The framing
is sound.

### 4. Does M29 make Barnes-Hut a V3 capability addition rather than a same-contract speedup row?

Yes, and the constraint is correctly enforced.

M29 classifies v2.14 as `v2_14_has_cpu_fused_or_typed_stream_only`. Specifically, v2.14
has `fused_frontier_force_sum_bucketized_cpu` and `grouped_vector_sum_typed_stream_plan`,
but it does not have the Numba CUDA fused route, the prepared-execution session runner, or
the aggregate-tree fused weighted-vector sum surface. These are V3 additions.

This means there is no equivalent v2.14 surface to run against for a same-contract speedup
comparison. The M67/M28/M29 evidence is about V3 adding GPU-accelerated Barnes-Hut
capability through a productized runner, where v2.14 had only CPU routes. A V3-over-v2.14
performance ratio would mix different contracts and create the overclaim M29 explicitly
forbids.

M45's note that "M28/M29 should not be used to claim that Barnes-Hut as an app is fixed"
is also correct and orthogonal: the runner-route evidence is capability evidence, not
all-app regression evidence. The boundary between these two is maintained.

### 5. Should Barnes-Hut be counted as an existing Step-1 material family?

Yes. The evidence meets the Step-1 counting standard, and accepting the count is the
correct call.

The Step-1 standard from the M28 report is: "a real aggregate-tree/vector-accumulation
route now flows through the productized runner without losing the existing fused partner
performance." All three necessary elements are present:

**V3 capability addition:** M29 confirms the Numba CUDA fused route and prepared-execution
runner did not exist in v2.14. This is a new GPU-accelerated capability path, not a
performance comparison against a comparable predecessor.

**Predecessor displacement:** The fused vector approach displaces the historical prepared
OptiX frontier route by `12.730691x` geomean. While this predecessor is itself V3-era
(not a v2.14 baseline), it represents a genuine elimination of a compressible phase — the
old frontier emission path — in favor of the fused approach. This is legitimate material
evidence within V3's engineering trajectory.

**Productized runtime parity:** The runner carries the high-performance route at
`0.999328x` geomean through the full productized trunk with internal device residency,
no host materialization, and verified output equivalence. The generic helper
(`run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`) has no Barnes-Hut
name in its body, confirming it is a reusable primitive rather than an app-specific
shim.

All 15 checks in the M67 packet pass with zero failures. No blocking issues are present
in the packet, the script logic, or the test suite. The `test_script_rebuilds_packet`
gate verifies the packet is fully reproducible.

**Carry-forward caveat:** Counting Barnes-Hut as a Step-1 material family does not close
the M45 all-app regression story. The frozen OptiX node-coverage rows (0.622x,
0.591x, 0.961x) remain in the scorecard, pending full-suite validation with the M24/M7
focused generic fix projected in. That regression closure is entirely separate from the
Step-1 counting question answered here.

**Carry-forward caveat:** The predecessor displacement (12.73x) is internal to V3
development and cannot be used as a public-facing V3-over-v2.14 speedup story. It is
valid as internal evidence that the fused approach was the right engineering direction,
but it must never become the primary public performance claim.

### 6. Are the non-authorization boundaries complete?

Substantially yes, but there is a gap between the M67 packet's formal `non_authorization`
dict and the call-for-review's full list.

The M67 JSON `non_authorization` covers: release, all-app run, paid POD spend, focused
POD spend, public speedup claim, broad V3-over-V2 claim, RT-core speedup claim,
true-zero-copy claim, and automatic partner selection. These are the critical flags.

The call-for-review additionally lists: watch-row closure, app-specific Barnes-Hut engine
tuning, whole-app speedup claim, and paper reproduction claim. The first two are covered
contextually — `new_barnes_hut_app_tuning_allowed: false` is in the `reconciliation`
block, and watch-row closure is implicitly excluded by `all_app_run_authorized: false`.
The whole-app speedup and paper reproduction exclusions are present in prior documents
(M45, M66 consensus) but are not formally enumerated in the M67 packet's own
`non_authorization` dict. This is a P2 gap: the critical flags are all closed, but the
formal dict does not mirror the full call-for-review list.

**P2 carry-forward:** The next packet that references M67 as an input should explicitly
enumerate watch-row-closure, app-specific-tuning, whole-app-speedup, and
paper-reproduction-claim as false in its own `non_authorization` section to close the
gap.

The `_non_authorization_flags_closed` check in the script validates sub-document flags
(runner, m29, step2) and passes. This is not a script defect; the gap is in the M67
packet's own enumeration, not in its downstream dependencies.

## Non-Authorization

This review does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- focused POD spend
- public speedup wording of any kind
- broad V3-over-V2 claim
- whole-app speedup claim
- paper reproduction claim
- RT-core speedup claim for the Numba CUDA fused route
- true-zero-copy claim
- automatic partner selection
- app-specific Barnes-Hut engine tuning
- watch-row closure

Accepting the Step-1 counting verdict means: Barnes-Hut is recorded as an existing
Step-1 material family based on the M28/M29 runner-parity and capability-addition
evidence. It does not mean the Barnes-Hut all-app regression is closed, that any
performance number may be published, that a POD run may begin, or that V3 is
releasable. The next engineering action is to select the next Set-A family. No
deviation from any of the above boundaries is authorized or implied by this review.
