# Gemini Independent Review: Goal4298/Goal4299 v2.11 Embree CPU + Numba Reference Path

**Date:** 2026-06-11

**Reviewer:** Gemini

## Verdict

`accept-with-boundary`

## Summary

The Goal4298 and Goal4299 work defines and validates the v2.11 Embree CPU and current-partner reference paths. This work establishes a clear, executable packet for the ten current benchmark applications, utilizing Embree CPU where applicable and a Numba CPU partner reference for cases without an Embree front door (specifically RTNN). The implementation rigorously enforces claim boundaries, explicitly disclaiming performance, release, zero-copy, or RT-core acceleration claims, emphasizing its role as a reference and compatibility update.

## Facts Verified

1.  **Registry Coverage:** The registry, as defined in `src/rtdsl/current_embree_cpu_partner_reference.py`, covers all ten current benchmark apps exactly once. This is explicitly listed and validated within the code and confirmed in `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md`.
2.  **Embree CPU vs. Numba Reference:** Nine rows correctly exercise Embree CPU. The `rtnn` row is designated as the sole Numba CPU partner reference, acknowledging the absence of an Embree front door for the current RTNN app. This distinction is clearly maintained in `src/rtdsl/current_embree_cpu_partner_reference.py` and detailed in `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md`.
3.  **Runner Behavior:** The runner script (`scripts/rtdl_v2_11_embree_cpu_partner_reference_runner.py`) correctly sets all-thread CPU environment variables, prints per-row progress, supports the `--only` flag for resumability, and robustly fails closed on claim-boundary flags.
4.  **Local Linux Validation:** The `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_local_linux.json` artifact confirms `all_pass: true` for all ten rows, indicating successful execution on the specified local Linux environment.
5.  **Goal4299 Genericity:** Goal4299 successfully adds generic `partner="numba"` support to `top_k_nearest_points_2d_partner_columns` within `src/rtdsl/partner_adapters.py`. This is achieved through Numba pairwise score rows followed by host-ranked reference top-k, without resorting to RTNN-specific shortcuts. The code and `docs/reports/goal4299_numba_topk_partner_reference_for_v2_11_embree_cpu_packet_2026-06-11.md` explicitly state that this is a correctness/reference path, not a performance-optimized one.
6.  **ANN App Change Scope:** The change to `examples/current/apps/ml/rtdl_ann_candidate_app.py` for Numba device columns is limited to output conversion (copying data to host and converting to list), confirming that it does not introduce complex Numba-specific logic beyond standard adapter interaction.
7.  **Claim Boundary Enforcement in Reports:** Both `docs/reports/goal4298_v2_11_embree_cpu_partner_reference_packet_2026-06-11.md` and `docs/reports/goal4299_numba_topk_partner_reference_for_v2_11_embree_cpu_packet_2026-06-11.md` consistently and explicitly state that the work does not authorize release, public speedup, broad RT-core, Intel GPU, true-zero-copy, automatic partner selection, or app-specific engine logic.

## Answers to Questions

1.  **Is the Embree CPU + Numba reference path correctly scoped for v2.11?**
    Yes. The work is appropriately scoped as a reference and compatibility path for v2.11. The documentation and code consistently disclaim any claims of new performance milestones or features, focusing instead on establishing a stable baseline.

2.  **Is the RTNN Numba path honest enough as a reference path, given that top-k ranking is still host-materialized after device score rows?**
    Yes, the RTNN Numba path is honest. The implementation in `src/rtdsl/partner_adapters.py` explicitly performs host-side ranking after Numba device score rows. The rationale for this (Numba grouped_topk_f64 device kernel not yet implemented) is clearly documented in `docs/reports/goal4299_numba_topk_partner_reference_for_v2_11_embree_cpu_packet_2026-06-11.md` and reflected in the metadata, making the current limitations and future goals transparent.

3.  **Do any names, docs, metadata, or tests overclaim performance, release readiness, zero-copy, or RT-core acceleration?**
    No. Across all reviewed files (code, reports, and metadata), a stringent approach to claim boundaries is observed. Explicit `claim_boundary` fields and boolean flags are consistently set to `False` or clearly indicate non-authorization for performance, release readiness, zero-copy, or RT-core acceleration claims.

4.  **Are there any correctness risks in the Numba top-k deterministic ordering or ANN output conversion?**
    No. The Numba top-k implementation within `src/rtdsl/partner_adapters.py` achieves deterministic ordering by transferring score rows to the host and then employing a stable sorting algorithm (by score, then item ID). The ANN output conversion in `examples/current/apps/ml/rtdl_ann_candidate_app.py` is a standard `copy_to_host().tolist()` operation, which is a correct and safe method for retrieving data from Numba device arrays.

## Recommendations

No further changes are required as the work fulfills its stated purpose as a reference and compatibility path, with clear and accurate boundary definitions.
