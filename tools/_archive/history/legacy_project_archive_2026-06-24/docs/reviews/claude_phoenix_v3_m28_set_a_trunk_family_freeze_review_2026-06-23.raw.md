Review saved. Here is the summary:

---

## Verdict: `approve_with_amendments`

No blocking findings. Four amendments required before M29 cites this freeze.

### Blocking Findings
None.

### Amendments Required

**Amendment 1 — `runtime_sourced_material_gain: true` is misleading in `summary.json`.** The runner/control geomean is 0.9993x (parity). The `true` value is attributable to the historical OptiX reference displacement (~12.73x), which is the no-go route. A future reader or script reading the JSON without the document context will misread this as a current-baseline material gain. The freeze packet and all M29 citations must explicitly state that this field is keyed to the historical reference, not the current runner vs. current fused control.

**Amendment 2 — `validation_skipped: true` on all 45 evidence rows is unexplained.** `validation_reason: "user_skip_validation"` appears on every single row. The summary-level equivalence check (`runner_control_equivalence_rows`) did run and passes, but the freeze packet never says what per-row validation was bypassed or why. One clarifying sentence is required — either that per-row validation is a schema check (not a correctness check) that is fully subsumed by the summary-level equivalence gate, or that it was skipped for another documented reason.

**Amendment 3 — "generic" in the frozen family name needs a one-line scope note.** "Generic" is accurate at the code level (the API is not Barnes-Hut-specific), but could be read as "validated with multiple apps." It has only been tested through the Barnes-Hut pressure app. Add a sentence clarifying that "generic" refers to API design, not multi-app coverage.

**Amendment 4 (carry-forward) — Re-state the `git_commit: null` provenance caveat.** The prior fixed review established this requirement. The M28 packet doesn't re-state it. M29 must record this in its report header.

### Answers to the Seven Questions (brief)

1. **Right first family?** Yes. RTDBSCAN is at 0.9976x (below the freeze packet's own floor), RayJoin has no material win. This is the only candidate with clean gates.
2. **Gates sufficient?** Yes (with Amendment 2 explanation applied). Runner, trunk execution, residency, no host materialization, output equivalence by count and checksum — all present and all passed.
3. **V2.14/current boundary honest?** Yes — the strongest part of the packet. The three-path classification system and the requirement to fresh-checkout before timing are the right structure.
4. **Parity bar (>=0.95x/row, >=0.98x geomean) strict enough?** Yes. Actual results are 0.9981-1.0005x per row; the floors only serve as stop conditions.
5. **Material gain floor (>=1.15x / >=1.20x) appropriate?** Yes. The freeze doesn't claim gain anyway; the floor governs future speed classification only.
6. **Hidden overclaims?** No RT-core, zero-copy, V4, or app-specific claims. The `runtime_sourced_material_gain: true` JSON field is the only near-miss (addressed by Amendment 1, not a blocker).
7. **Should M29 proceed as written?** Yes, with the four amendments applied. Sequencing (Barnes-Hut → second Set-A family → all-app) is correct.
on was skipped or why.

The summary-level equivalence check (`runner_control_equivalence_rows`) did run and passes at all three sizes — contribution count, checksum_force_x, and checksum_force_y match exactly between runner and control. That check is sufficient for the equivalence gate. However, `user_skip_validation` on every row leaves open the question of what the per-row validation pass would have checked and whether skipping it exposed any gap.

Required fix: The freeze packet or an M29 amendment note must document (one sentence) what the per-row `validation` step would have verified and explicitly confirm that the summary-level `runner_control_equivalence_rows` check fully covers what was skipped. If the per-row validation is a format/schema check rather than a correctness check, say so.

### Amendment 3 — Clarify the meaning of "generic" in the frozen family name

The frozen family name is `generic aggregate-tree fused weighted-vector sum 2D, explicit Numba CUDA partner, routed through prepared_execution_session_runner`. The freeze packet states "The frozen runtime family is not Barnes-Hut-specific." At the code level this is accurate: `run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session` is written as a general-purpose primitive, not a Barnes-Hut-specific kernel.

However, the word "generic" in a frozen family name could be read as "validated with multiple apps," which it has not been. The only pressure app evidence is Barnes-Hut.

Required fix: Add one sentence to the M28 freeze packet clarifying that "generic" refers to the API design of the runner primitive (it accepts any compatible input, not Barnes-Hut-specific kernel code), not to multi-app test coverage. Multi-app coverage belongs to all-app timing in M30+.

### Amendment 4 (carry-forward) — Re-state the `git_commit: null` provenance caveat

The prior fixed review (second-AI, 2026-06-22) required: "Final reporting must include provenance honestly rather than inventing a commit." The evidence `summary.json` confirms `"git_commit": null` because the remote tree (`/root/rtdl_v3_rebuild_20260620/current` on `213.173.108.14:11592`) is not a git checkout. The M28 freeze packet cites the evidence directory but does not re-state this caveat.

Required fix: M29 must re-state in its report header that the evidence base commit is the local git commit (`8e0f052bffec02507aaf5ed05f75dfe995f39883`) and that the remote execution tree has `git_commit: null`. This must not be omitted in any document that cites this evidence for Set-A credit.

---

## Answers to the Seven Questions

### Q1. Is Barnes-Hut aggregate-tree fused weighted-vector sum the right first true Set-A family to freeze, given the RTDBSCAN/RayJoin history?

Yes. The evidence record for the alternatives does not support displacing this choice:

- RTDBSCAN M3.4 recovered to 0.9976x runner/legacy — below the >=0.98x geomean floor the freeze packet would itself impose. That route has no material gain and failed a strict parity test on first attempt before recovering only to parity.
- RayJoin has structural runner evidence but no demonstrated material runtime-sourced win and no comparable focused POD A/B packet with clean gates.

Barnes-Hut aggregate-tree fused vector accumulation has: a fixed POD run with clean gates, a passed parity bar at all three body counts, consistent residency metadata on every runner sample, and output equivalence confirmed at the checksum level. It is the only current candidate that has passed all the gates this freeze packet specifies. The choice is correct given the available evidence.

The one legitimate concern is that this is a single pressure app. That concern is addressed by the requirement that a second Set-A family (M30) must be accepted before all-app timing begins.

### Q2. Are the proposed gates sufficient to prove that the productized V3 runtime trunk actually executes and preserves internal residency?

Yes, with the explanation caveat from Amendment 2 applied. The required gates — runner used, trunk executes end-to-end, internal device residency between RTDL phases, no frontier/contribution/hot-path host materialization, output equivalence by count and checksum — are the right set. All pass in the raw evidence.

One note on scope: these gates prove that the productized runner path carries the fused Numba CUDA route without regressing performance and without leaking intermediate data to host. They do not prove correctness of the broader V3 runtime for other families or all-app contexts. That is the correct scope for a single-family Set-A freeze.

### Q3. Is the V2.14/current boundary honest enough, especially the warning that v2.14 node-coverage and current fused force-vector continuation are not the same contract?

Yes — this is the strongest part of the freeze packet. The three-path classification (`v2_14_lacks_current_trunk_surface`, `v2_14_has_equivalent_fused_surface`, `v2_14_has_only_node_coverage_or_frontier_route`) is precisely the right structure. Requiring M29 to perform a fresh checkout and classify before timing — rather than assuming a same-contract baseline — avoids the V3-over-V2 overclaim failure mode that was identified as the primary risk in the RTDBSCAN history.

The warning that v2.14 node-coverage and current fused force-vector continuation are not the same contract is stated clearly and backed by specific evidence: the current mode names (`fused_frontier_force_sum_bucketized_numba_cuda`, `prepared_execution_fused_vector_sum_numba_cuda`) and the current session runner function (`run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session`) are all absent from v2.14. V2.14's Barnes-Hut evidence centers on prepared fixed-depth node-coverage, not fused force-vector continuation. This is correctly treated as a different contract.

### Q4. Is the current-runner vs current-fused-control parity bar (>=0.95x every row, geomean >=0.98x) strict enough for runner productization?

Yes. The floor is appropriate for a productization gate. The actual results (1.0005x, 0.9993x, 0.9981x per row; geomean 0.9993x) sit so far above both floors that the floors only matter as stop conditions. Any runner regression that pushes a row below 0.95x against the current fused partner would represent a 5% wall-time loss on a hot path, which is a genuine regression for a productized route.

The combined use of a per-row floor AND a geomean floor is the right structure: the per-row floor prevents a single severe outlier from being hidden in a favorable geomean, while the geomean floor catches several mild but consistent regressions.

### Q5. Is the material-gain floor (>=1.15x, preferred >=1.20x) appropriate for any speed classification?

Yes. This freeze does not claim material gain for the runner itself — the runner achieves parity with the current fused control, not a speedup over it. The 1.15x/1.20x floor applies only to future speed classification work (e.g., if M29 finds an equivalent V2.14 route and the current runner beats it).

At 1.15x geomean, a speed claim requires the runner to be materially faster than the baseline, not merely at noise-level advantage. The 1.20x preferred threshold adds a meaningful margin over 1.15x to distinguish signal from measurement noise at these wall times (~10-40ms hot calls with 5 samples). Both floors are appropriate.

### Q6. Are there hidden app-specific, RT-core, zero-copy, or V4 overclaims in the freeze packet?

No hidden overclaims of those types. The Numba CUDA mode does not use RT cores, and the packet contains no RT-core speedup claim (`rt_core_speedup_claim_authorized: false` on every row). No zero-copy claims are present (`true_zero_copy_claim_authorized: false` everywhere, `v4_embedding_or_external_zero_copy_authorized: false` everywhere). No V4 scope is invoked. The `native_engine_app_specific: false` flag is set correctly on all rows.

One near-miss that is not a hidden overclaim in the document text but requires Amendment 1: `runtime_sourced_material_gain: true` in the summary JSON is technically attributed to the historical OptiX reference displacement (12.73x geomean over the no-go route), not the runner vs. current fused control (0.9993x). The freeze packet correctly labels the historical leg as a no-go reference in prose, but the JSON field alone could mislead a reader who inspects the summary without the document. This is addressed by Amendment 1 and is not a hidden overclaim in the document text itself.

### Q7. Should M29 proceed as written, or should the family choice be revised before spending more POD time?

M29 should proceed as written, with the four amendments above applied. The v2.14/current Barnes-Hut classification is the correct next step. The cost estimate (0.5-1.5 POD hours, approximately $0.13-$0.38) is consistent with the scope of a focused checkout-and-classify run.

The sequencing is correct: M29 classifies v2.14/current Barnes-Hut; M30 identifies and probes the second Set-A family (RTDBSCAN resident-component continuation or RTNN-style resident graph/partner path); only after two accepted Set-A families does a serious all-app V2.14/current run become permissible. That gate is the right gate.

One addition recommended for M29: if the v2.14 classification resolves to `v2_14_lacks_current_trunk_surface`, M29 should explicitly record the `git_commit: null` provenance gap and confirm whether the local base commit (`8e0f052bffec02507aaf5ed05f75dfe995f39883`) is sufficient to anchor the M28 evidence for citation purposes. The prior review's provenance note must not be silently inherited; it must be re-stated.

---

## Evidence Cross-Check

Raw data verified from `summary.json`. Runner vs. current fused control parity rows:

| Bodies | Runner median (s) | Control median (s) | Ratio | >=0.95x pass |
| ---: | ---: | ---: | ---: | :---: |
| 32,768 | 0.010791808 | 0.010797493 | 1.000527x | yes |
| 65,536 | 0.015773401 | 0.015763111 | 0.999348x | yes |
| 131,072 | 0.041481458 | 0.041403107 | 0.998111x | yes |

Geomean runner/control: 0.999328x. Geomean floor >=0.98x: passes.

Output equivalence at all three body counts: checksum_force_x, checksum_force_y, and contribution_row_count match exactly between runner and control median values. `equivalence_pass: true` for all three sizes.

Internal device residency: `internal_device_residency_all_samples: true` for all three runner body-count groups in `variant_size_summaries`. This field is `false` for all control and historical rows, as expected.

Failed checks: `[]`. All 14 named checks are `true`.

Claim flags: all `false` at both row level and summary level, including `public_speedup_claim_authorized`, `release_authorized`, `broad_v3_faster_than_v2_claim_authorized`, `true_zero_copy_claim_authorized`, `wrapper_itself_faster_than_existing_fused_partner_claim_authorized`, `full_all_app_rerun_authorized_by_this_packet`.

The checksum values for the runner variant are stable across all five samples (single unique value per body count per summary). The historical OptiX variant shows small variation in checksums across samples (expected for non-deterministic ray-tracing emission ordering), confirming it is not being compared for correctness purposes.

---

## Non-Authorization Block

This review authorizes no Phoenix V3 release. It authorizes no all-app run. It authorizes no public speedup claim. It authorizes no broad V3-over-V2 claim. It authorizes no RT-core speedup claim. It authorizes no true-zero-copy claim. It authorizes no V4 work. It authorizes no automatic partner selection. The approval granted here is limited to: accepting the M28 freeze packet as a valid first Set-A runtime-trunk family freeze candidate, conditional on the four amendments above being applied, and permitting M29 to proceed with the v2.14/current Barnes-Hut classification run as scoped in the freeze packet.
