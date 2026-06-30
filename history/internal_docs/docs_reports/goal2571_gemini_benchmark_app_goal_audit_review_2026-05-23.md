Verdict: ACCEPT

The Goal 2571 Benchmark-App Goal Audit accurately synthesizes the development and cleanup sequence from Goal 2392 through Goal 2570. Repository evidence confirms that all specified review and consensus requirements have been met for the current internal snapshot.

### Key Verification Findings

*   **Robot Goal 2491 Consensus:** The requirement for at least 2-AI consensus stated in the Goal 2491 closeout was satisfied and exceeded by the Goal 2529 3-AI consensus (`ACCEPT-WITH-BOUNDARY` from Codex, Claude, and Gemini).
*   **Barnes-Hut Coverage:** Goal 2550 (Barnes-Hut closeout) and Goal 2551 (3-AI Rethink) confirm that Barnes-Hut is fully covered by the current consensus. Goal 2549's rejection of app-specific native force math is correctly identified as a critical boundary preservation step.
*   **Goal 2551 Findings Addressal:** The cleanup ledger in Goal 2571 is supported by the implementation reports (Goals 2552-2570). Specifically:
    *   **Goal 2552** added the missing `overflowed_out` signal to grouped reduction APIs.
    *   **Goal 2553** renamed internal native `DbScan` terms to generic `ColumnarPredicateScan` names.
    *   **Goal 2562 & 2563** successfully moved robot-collision and Barnes-Hut specific adapters out of the shared `rtdsl.partner_adapters` core.
    *   **Goal 2566** produced a machine-readable evidence manifest that matches the repository state.
*   **Compatibility DB Aliases:** The remaining `RtdlDb*` aliases in `src/native/optix/rtdl_optix_prelude.h` are correctly documented as intentional compatibility debt. They are appropriately fenced by the audit's claim boundaries, which prevent claims of total ABI "purity" or external stability.
*   **Public Claims Authorization:** There is no evidence of over-authorized public release or performance claims. Every closeout report (Goal 2478, 2491, 2520, 2550) and the final evidence manifest (Goal 2566) contains explicit, multi-layered disclaimers against paper reproduction, broad speedup wins, and authors-code parity claims.

### Constraints

*   **Snapshot Identity:** The `internal-benchmark-apps-2026-05-23` label must be strictly maintained for all current artifacts.
*   **Claim Boundary:** Adhere to the "Blocked" wording list in Goal 2571, specifically regarding the avoidance of "product," "solver," or "DBMS" terminology for these research reconstruction instruments.
*   **ABI Stability:** No external ABI stability should be claimed for the `DeviceColumnDescriptor` or `grouped_reduction.v1` substrates until further native migration and stabilization cycles are completed.
