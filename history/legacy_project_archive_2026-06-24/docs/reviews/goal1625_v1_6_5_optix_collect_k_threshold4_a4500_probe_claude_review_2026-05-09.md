## Verdict

**ACCEPTED** — as internal same-host RTX A4500 OptiX collect-k threshold-4 diagnostic evidence only.

---

## Checked Evidence

**Copy-reduction regions (65537, 65538, 65552, 69632) — consistently favorable:**

| Count | Baseline copies | Gated copies | Median delta ms | Faster rounds | Parity |
|------:|----------------:|-------------:|----------------:|--------------:|--------|
| 65537 | 5 | 0 | −0.0236 | 5/5 | True |
| 65538 | 5 | 0 | −0.0222 | 4/5 | True |
| 65552 | 5 | 0 | −0.0220 | 4/5 | True |
| 69632 | 4 | 0 | −0.0178 | 5/5 | True |

All four copy-reduction counts pass the test-enforced gates: `gated_payload_copies < baseline_payload_copies`, `median_delta_ms < 0.0`, `faster_rounds ≥ 4`, `all_parity = True`.

**No-copy-reduction controls (65536, 69633) — not claim-worthy, correctly bounded:**

- **65536** (0 copies both sides): avg delta +0.016 ms, median +0.027 ms, faster_rounds = 1/5 — gated is slower or neutral; test enforces `median > 0` and `faster_rounds ≤ 1`. Correct control.
- **69633** (4 copies both sides, gate does not fire): median delta −0.00188 ms; test enforces `abs(median) < 0.005`. Near-zero and treated as a control, not a performance claim. Note: round 3 shows a baseline spike (0.354 ms vs ~0.313 ms typical) inflating avg delta to −0.009 ms and producing 4/5 faster rounds — but the median bound holds, and no claim is derived from it.

**Parity:** `all_parity = True` across all 6 counts × 5 rounds × both arms. No correctness regression.

**Claim flags:** All six flags (`public_speedup_wording_authorized`, `true_zero_copy_wording_authorized`, `stable_collect_k_promotion_authorized`, `broad_rtx_gpu_wording_authorized`, `whole_app_speedup_claim_authorized`, `release_action_authorized`) are `false` in both the JSON artifact and the script source. The claim boundary string is present verbatim in both the JSON and the rendered markdown.

**Test suite alignment:** `test_a4500_artifact_records_strong_copy_reduction_regions`, `test_a4500_artifact_keeps_no_copy_reduction_controls_non_claimed`, and `test_a4500_artifact_blocks_public_claims` collectively enforce all three structural requirements. No test asserts a public or stable claim.

---

## Blockers

None.

---

## Claim Boundary

This evidence authorizes exactly: *gated collect-k with threshold-4 produces fewer payload copies and lower latency than the optimized baseline at the tested copy-reduction counts, on a single RTX A4500 host running RTDL v1.6.5 OptiX, at commit `30c8cb9b`.*

It does **not** authorize: public speedup wording, true zero-copy wording, stable `COLLECT_K_BOUNDED` promotion, broad RTX/GPU wording, whole-app speedup claims, release tags, or any release action.
