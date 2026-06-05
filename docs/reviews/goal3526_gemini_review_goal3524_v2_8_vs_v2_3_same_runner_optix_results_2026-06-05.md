# Gemini Review For Goal3524 v2.8 vs v2.3 Same-Runner OptiX Results

Date: 2026-06-05

## Review of Goal3524: v2.8 vs v2.3 Same-Runner OptiX Results

This review addresses Goal3524, which provides an internal A5000 same-runner OptiX comparison between v2.3 and v2.8. The review is based on the provided report (`docs/reports/goal3524_v2_8_vs_v2_3_same_runner_optix_results_2026-06-05.md`), compact results JSON (`docs/reports/goal3524_pod_artifacts/goal3524_compact_results.json`), and the test file (`tests/goal3524_v2_8_vs_v2_3_same_runner_optix_results_test.py`), as well as the protocol defined in `docs/reports/goal3523_v2_8_vs_v2_3_same_contract_comparison_protocol_2026-06-05.md`.

### 1. Verification of A5000 Same-Runner OptiX Scope

The report and compact results JSON consistently verify the A5000 same-runner OptiX scope:
- **v2.3 evidence commit:** `2a28365d0246d51f3e3322b546f8a68c58632db4`
- **v2.8 commit:** `d266b0370bcbcd4cbc24006ce9de2dfe783c1d2e`
- **GPU:** NVIDIA RTX A5000.
These details align across all relevant documents.

### 2. Verification of All Rows and Summary Statistics

All 11 rows are confirmed `ok` in both v2.3 and v2.8 versions within the compact results. The summary statistics from the report are accurately reflected in the compact results JSON:
- **Rows:** 11
- **v2.8 wins:** 6
- **v2.8 losses:** 5
- **Geometric mean speedup:** 1.138x (actual 1.1379687921762345)
- **Median speedup:** 1.002x (actual 1.0020696683182604)
- **Best row:** 7.202x (`raydb_optix_partner_resident_sum`) (actual 7.201679979392616)
- **Worst row:** 0.401x (`barnes_hut_optix_node_coverage`) (actual 0.4006197432630818)
All figures are consistent.

### 3. Verification of Weak Rerun Interpretation

The weak rerun results confirm the interpretation in the report:
- **Barnes-Hut node coverage:** Confirmed as a real regression, showing 0.401x in the standard run and 0.503x in the weak rerun.
- **Contact manifold and triangle counting:** Confirmed as near-parity/noise rows, showing slight variations around 1.0x speedup in both standard and weak reruns, with speedup values of 0.973x (standard) and 1.030x (weak rerun) for contact manifold, and 0.992x (standard) and 1.025x (weak rerun) for triangle counting.

### 4. Verification of Claim Boundary

The report explicitly states that Goal3524 does not authorize any public v2.8 release wording, public speedup wording, whole-app speedup wording, broad RT-core speedup wording, package-install or PyPI wording, true zero-copy wording, or paper reproduction claims. The `claim_boundary` section in the compact results JSON corroborates this, with all relevant authorization flags set to `false` and `internal_results_only` set to `true`.

### 5. Sufficiency for Internal Comparison and Blocks for Public Comparison

This Goal3524 packet is sufficient for an internal same-runner OptiX comparison slice, as it provides clear, reproducible evidence for internal evaluation.

However, several factors still block a final v2.8 public comparison:
- **Barnes-Hut regression:** The significant regression in Barnes-Hut node coverage requires investigation.
- **Comparison approach for evolved contracts:** A decision is needed on whether the final v2.8 comparison should only include same-runner tables or also incorporate a second table for evolved contracts where app behaviors have intentionally changed since v2.3.
- **External review:** The report recommends seeking external review of this Goal3524 packet before its use in any release narrative.

## Verdict

`accept-with-boundary`

The Goal3524 results provide valuable internal evidence of v2.8 performance relative to v2.3 for the specified OptiX same-runner cases on A5000 hardware. The comparison is complete and reproducible, identifying both improvements and a significant regression (Barnes-Hut). It clearly delineates the scope of its claims, preventing unauthorized public statements. The identified next steps and blocking issues are appropriate for moving towards a comprehensive v2.8 public comparison.