---

## Independent Review: Goal1612 v1.6.3 Linux Backend Bridge Evidence Addendum

---

### Verdict

**ACCEPTED** as Linux backend bridge evidence for the prepared host-output measurement path.

---

### Findings

**Artifact integrity**

- Git commit `527d38e1a5fb0fb6d63015c0bbabdd7a7b15bf8c` is consistent across the evidence addendum, all three JSON records, and the review context. No hash drift.
- Host (`lx1`), platform (`Linux-6.17.0-20-generic-x86_64-with-glibc2.39`), and Python (`3.12.3`) are uniform across all records.
- Native library chain of custody is recorded: `build/librtdl_embree.so` and `build/librtdl_optix.so` observed before run; runtime probes confirmed Embree `(4,3,0)` and OptiX `(9,0,0)`.
- Command line in the addendum matches JSON parameters (`unique_rows=64`, `repeats=4`, `iterations=5`), producing `candidate_row_count=256` (64×4). Arithmetic is consistent.

**Required backend handling**

- `required_backends = [fake_native, embree, optix]` matches `backends`; no optional-skip loophole.
- All three records carry `status: pass`. `skipped_required: []`, `failed: []`, `accepted: true`, `status: accepted_backend_bridge`. No gaps.

**Materialization counters**

All three backends report identical, internally consistent counters:

| Field | Value | Expected |
|---|---|---|
| `baseline_input_materialization_count` | 5 | = iterations ✓ |
| `prepared_input_materialization_count` | 1 | once and held ✓ |
| `input_materialization_count_delta` | 4 | 5 − 1 ✓ |
| `prepared_host_output_buffer_reused` | `true` | required ✓ |
| `timing_recorded_for_diagnostics_only` | `true` | required ✓ |
| `copy_counts.prepared_buffer_reuse_count` | 5 | = iterations ✓ |
| `host_to_device_copy_count` | 0 | host-output path ✓ |

**Claim boundary**

- All 8 `claim_flags` are `false` at three levels: top-level JSON, manifest, and per-record. No flag is missing or toggled.
- Claim boundary text is identical at all three levels (no drift between manifest, top-level, and records).
- Boundary explicitly denies: performance claims, public speedup wording, whole-app speedup, broad RTX wording, true zero-copy, stable COLLECT_K_BOUNDED promotion, partner tensor handoff, package install, release tag, release action.

**Overclaiming check**

- Evidence addendum unambiguously labels GTX 1070 as "smoke/behavior environment only" and states the run "is not RTX performance evidence."
- Timing fields are null for GPU-transfer phases (device/host transfers, traversal), consistent with a host-output bridge on a non-RTX card.
- The MD report verdict line says "ACCEPTED as backend bridge evidence." — no stronger claim.

**Test file (`tests/...bridge_test.py`)**

- `test_linux_backend_bridge_artifact_accepts_all_required_backends` reads the live JSON and asserts: `accepted`, `skipped_required=[]`, `failed=[]`, all records `pass`, all claim flags `false`, GTX 1070 smoke wording present, "not RTX performance evidence" present. These checks are structurally sufficient for this evidence tier.
- `test_validator_rejects_claim_and_path_comparison_regressions` covers four guard paths: claim flag flip, negative delta, timing flag removal, output buffer reuse removal. Validator coverage is adequate.
- `test_external_review_artifacts_record_acceptance` depends on three external review files in `docs/reviews/`; these are not among the new untracked files, implying they were committed in a prior step. Windows run of 36 tests passes, confirming those files exist and contain the required strings.
- The modified test file does not weaken any existing assertion; it adds Linux-artifact validation only.

---

### Required Fixes

None. No integrity failures, no counter arithmetic errors, no overclaiming, no claim flag regressions, no missing required-backend enforcement.

---

### Acceptance Notes

- This evidence is scoped correctly: it proves the prepared host-output measurement path reaches and executes all three backends on local Linux. It makes no inference about performance, speedup ratios, or RTX behavior.
- The GTX 1070 / smoke-environment labeling is explicit in both the addendum and the test assertions, preventing misuse as RTX or public-benchmark evidence.
- If this artifact is later cited in a higher-tier review, the reviewer should confirm the three external review files (`claude_review`, `gemini_review`, `3ai_consensus`) are present and contain the expected acceptance strings, since the test that guards them depends on committed files not visible in this diff.
- No action is required before accepting this addendum for its stated purpose.
