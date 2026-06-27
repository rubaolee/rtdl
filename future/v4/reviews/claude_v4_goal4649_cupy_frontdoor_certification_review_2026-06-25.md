## Review: V4 Goal4649 CuPy Front-Door Certification Gate

---

### Evidence Assessment

**Gate script denominator** — The corrected `_run_one_target()` loops over every `row_count` input row (lines 176–183 of the gate script), not groups. The goal-level audit documents the previous group-loop error and confirms the correction was applied before this run. Recorded as `cpu_row_loop_seconds` in both evidence rows. Denominator is honest for its stated purpose.

**POD evidence** — Both rows present in `pod_live_summary.json` with complete fields: `correctness_parity=true`, `max_err_x=0.0`, `max_err_y=0.0`, `host_materialization_in_hot_path=false`, `representative_speedup` well above the frozen `1.20x` floor (1716.8x and 2390.9x). Environment block records GPU, driver, CuPy version, Python, CUDA runtime, nvidia-smi output. `row_offset_validation_performed_at_prepare=true` for both rows.

**Claim boundary flags** — Every claim boundary field is present and false in metadata: `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `whole_app_speedup_claim_authorized`, `direct_device_handoff_authorized`, `v2_5_release_authorized`, `public_claim_authorized`, `cupy_performance_claim_authorized`. AM1 flags (`partner_migration_counts_as_v4_speed_win`, `partner_parity_counts_as_v4_speed_win`) are false in both the payload root and per-target entries.

**Target separation** — `v4_cupy_certification.py` correctly marks `cupy_segment_polygon_hitcount_prepared_scaling` and `cupy_hausdorff_witness_continuation` as `requires_v4_adapter_mapping_before_pod` with `v4_frontdoor_route=None` and unfrozen denominators. `v4_goal4649_ready_cupy_targets()` filters them out. Test suite verifies this separation explicitly.

**Tests** — 13 tests ran OK locally. `v4_goal4649_cupy_certification_gate_test.py` covers: target matrix separation, frozen bars on ready targets, front-door export, dry-run non-authorization. `v4_goal4649_cupy_certification_pod_evidence_test.py` covers: gate pass status, environment fields, per-row correctness/floor/metadata assertions.

**Goal4648 chain** — `goal4648_completion_consensus_2026-06-25.md` confirms fail-open bug was fixed and Goal4649 was properly authorized. Fail-closed contract is in place.

---

### Questions Answered

**Q1 — Is Goal4649 complete enough to start Goal4650?**  
Yes. Two ready targets passed the POD gate under the Goal4648 fail-closed contract, with frozen bars, correct denominator, and no public claims. The certification surface is narrow but complete. Goal4650 may start.

**Q2 — Do the two rows legitimately certify a narrow `grouped_vector_sum_f64x2` partner front-door surface?**  
Yes. Two representative sizes (262144/1024 and 524288/2048) passed with zero correctness error and speed ratios far above the frozen floor. The `warp_per_group_tiled` kernel uses presegmented offsets and a reused prepared session. This is a legitimate, narrow certification of one operator at two scales — not broad CuPy support.

**Q3 — Is it correct that Hausdorff/hitcount CuPy remain mapping debt, not support?**  
Yes. Both are code-visible in `v4_cupy_certification.py` with `gate_status=requires_v4_adapter_mapping_before_pod`, `v4_frontdoor_route=None`, and unfrozen denominators. They do not appear in the ready target list and are not referenced in the gate script run. The separation is correct and tested.

**Q4 — Is the denominator honest enough for a certification floor check?**  
Yes. The corrected denominator is a full Python row-loop over all `row_count` rows; this is documented in the script comment and the goal audit. The ratios (1716x and 2390x) are large but plausible for a synchronous-Python loop vs. a CUDA warp-reduction kernel with prepared session reuse. The report explicitly prohibits using these ratios as public speedup wording; they serve only as a floor gate. Denominator is honest for that purpose.

**Q5 — Are the evidence fields sufficient?**  
Yes. Correctness (zero error, boolean parity), scale (two row counts), denominator (labeled `cpu_row_loop_seconds`, denominator field describes it), environment (GPU, driver, CuPy, Python, CUDA runtime, nvidia-smi), hot host-materialization flag (false, checked at three metadata keys), claim boundaries (all false, per row and per payload). No field is missing for the stated certification scope.

**Q6 — Does this preserve AM1: partner migration/parity cannot become V4 speed evidence?**  
Yes. `partner_migration_counts_as_v4_speed_win=false` and `partner_parity_counts_as_v4_speed_win=false` appear in the payload root, in each ready-target record, and are asserted in both test files. AM1 is preserved end-to-end.

**Q7 — Should any public catalog/docs be updated now, or should promotion wait for Goal4651?**  
Wait for Goal4651. The goal report, the POD markdown, and the non-authorization list all agree that CuPy does not enter the public measured Tier-2 operator catalog before Goal4651 catalog gate. No public catalog or doc update should be made on the basis of this goal alone.

---

### Non-Authorization Preserved

All non-authorization boundaries from the call for review are intact across all files: no public release wording, no broad speedup language, no app-level comparison claims, no blanket CuPy support, no RT-core Tier-2 CuPy, no Hausdorff or hitcount CuPy, no arbitrary Numba callback, no C ABI/embedding, no true-zero-copy, no partner migration/parity as speed evidence.

---

## Verdict

```
accept_goal4649_complete
```
