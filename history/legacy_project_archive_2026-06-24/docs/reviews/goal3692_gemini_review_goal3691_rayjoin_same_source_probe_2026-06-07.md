# Independent Gemini Review: Goal3691 RayJoin Same-Source Probe

**Date:** 2026-06-07

**Reviewer:** Gemini CLI

**Verdict:** accept

## Summary of Findings

Goal3691 provides a crucial diagnostic comparison between RTDL and the original RayJoin implementation using the same bundled Brazil sample files. The report clearly distinguishes this effort from a full RayJoin paper reproduction or public performance claim, focusing instead on internal engineering conclusions.

The review confirms that:
*   RTDL's cross-map PIP shows promising query-time performance (1.868x speedup) against RayJoin but lacks count validation due to RayJoin's output limitations.
*   RTDL's LSI implementation is identified as a correctness/performance blocker, being significantly slower (0.075x speedup, i.e., ~13x slower) and exhibiting a one-intersection count mismatch.
*   The script adheres to app-agnostic RTDL engine boundaries and avoids introducing RayJoin-specific native logic, aligning with project conventions.
*   The report and artifact explicitly limit claims, strictly avoiding public speedup, release, or paper reproduction statements.
*   The recommended next steps are well-justified and directly address the identified LSI discrepancies.

## Key Facts Verification

All key facts provided in the prompt have been verified against the `summary.json` artifact and the `goal3691_rayjoin_original_same_source_probe_2026-06-07.md` report.

*   **RTDL source commit:** `c8f9adf0`, `goal3691_scoped_source_dirty=false`. **(Confirmed)**
*   **RayJoin source commit:** `02bf622`, with dirty checkout `M src/util/markers.h` and `?? release/` due to an include-path repair. **(Confirmed)**
*   **Same files used:** `/root/RayJoin/test/dataset/br_county_clean_25_odyssey_final.txt` (county) and `/root/RayJoin/test/dataset/br_soil_ascii_odyssey_final.txt` (soil). **(Confirmed)**
*   **PIP Metrics:**
    *   RayJoin query time: `0.000879685 s`
    *   RTDL query time: `0.000471005 s`
    *   RTDL/RayJoin query speedup: `1.8677x`
    *   RayJoin PIP count parity not established. **(All Confirmed)**
*   **LSI Metrics:**
    *   RayJoin query time: `0.000897010 s`
    *   RTDL query time: `0.011885975 s`
    *   RTDL/RayJoin query speedup: `0.0755x`
    *   RayJoin checked intersections: `20860`
    *   RTDL row count: `20859`
    *   Delta: `-1`. **(All Confirmed)**

## Questions Answered

1.  **Is the report honest that PIP is promising but not fully count-validated against RayJoin?**
    *   **Answer:** Yes. The report markdown and the `summary.json` explicitly state that PIP shows promising query time but lacks count validation due to RayJoin's `query_exec` output not printing the PIP hit count.

2.  **Is the report honest that LSI is a correctness/performance blocker, not a win?**
    *   **Answer:** Yes. The report clearly identifies LSI as a blocker due to significantly slower performance and a one-intersection count mismatch. The `summary.json` data supports this conclusion with a speedup factor of `0.075x` and a delta of `-1`.

3.  **Does the script preserve app-agnostic RTDL engine boundaries and avoid adding RayJoin-specific native logic?**
    *   **Answer:** Yes. The `scripts/goal3691_rayjoin_original_same_source_probe.py` reuses generic RTDL components and explicitly defines `_claim_boundary()` to set RayJoin-specific claims to `False`. This aligns with the principles outlined in `docs/research/future_version_to_do_list.md` regarding keeping the native engine generic and avoiding implicit RayJoin/CDB ownership semantics.

4.  **Does the artifact support only the limited internal conclusion and avoid release/public/RayJoin-paper/RTDL-beats-RayJoin/broad-RT-core/zero-copy claims?**
    *   **Answer:** Yes. The "Boundary" section of the report, the `claim_boundary` fields in `summary.json` (all set to `false`), and the validation in `tests/goal3691_rayjoin_original_same_source_probe_test.py` all unequivocally confirm that the artifact supports only internal engineering conclusions and explicitly avoids broader claims.

5.  **Are the recommended next steps correct: localize the missing LSI intersection and compare RTDL's predicate to RayJoin's scaled/high-precision predicate?**
    *   **Answer:** Yes. The "Next Work" section of the report lists these as the immediate and appropriate next steps to diagnose the LSI discrepancy, which is a critical blocker. This approach is consistent with the need to understand predicate differences, as hinted at in the `future_version_to_do_list.md`.

## Conclusion

The Goal3691 RayJoin same-source probe report, script, and artifact are well-executed, honest, and adhere to appropriate claim boundaries. The identified LSI correctness and performance blocker, along with the proposed next steps for investigation, are sound and necessary for future development.