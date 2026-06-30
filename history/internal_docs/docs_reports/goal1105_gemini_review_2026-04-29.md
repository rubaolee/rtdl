# Goal1105 Gemini Review 2026-04-29

**Verdict:** All conditions reviewed for Goal1105 are met and accurately reported.

**Details:**

*   **Linux Baselines Validity and Current-Contract:** The three completed Linux baselines (`barnes_hut_depth8_4096_embree_validation_baseline.json`, `facility_recentered_2_5m_cpu_oracle_baseline.json`, `facility_recentered_2_5m_embree_baseline.json`) are valid according to their JSON schema (`goal1101_current_contract_non_optix_baseline_v1`) and are confirmed to be "same-current-contract" by matching the `source_commit` hash (`cf22fb302bbd85afaa8ea6f9e2da26d278313635`) with the Goal1105 report.
*   **Goal1102 Report (3 ok / 1 missing):** The Goal1102 intake reports (`goal1102_current_contract_baseline_intake_2026-04-29.json` and `.md`) correctly state `ok_count: 3` and `missing_count: 1`, accurately reflecting the status of the baselines.
*   **Barnes-Hut 20M Failure (Signal-9 Memory Boundary):** The log for the Barnes-Hut 20M Embree timing row (`barnes_hut_20m_embree_timing.log`) clearly indicates "Command terminated by signal 9" and a "Maximum resident set size (kbytes): 15180436", confirming the failure was due to a signal-9 (SIGKILL) memory boundary, as stated in the Goal1105 report.
*   **Facility CPU vs Embree Timing Interpretation:** The interpretation in the Goal1105 report, noting that the CPU oracle is faster than Embree for the Facility contract (8.997 s vs 29.807 s median native query), is consistent with the data found in the respective JSON baseline files. This interpretation is honest and correctly identifies an impediment to certain RTX speedup claims for this contract.
*   **No Public RTX Speedup Claim Authorized:** The Goal1105 report and all individual baseline JSON files explicitly state that no public RTX speedup claims are authorized. This is consistently maintained across all documentation.

The baseline set remains incomplete due to the missing Barnes-Hut 20M Embree timing row, as noted in the Goal1105 report.
