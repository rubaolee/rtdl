# Goal988 Gemini Review 2026-04-26

**Review Decision:** ACCEPT

**Concrete Reasons:**

1.  **Semantic Correctness of `count_threshold_reached` with `HOTSPOT_THRESHOLD + 1`**:
    The approach of using `HOTSPOT_THRESHOLD + 1` for the `threshold` argument in `prepared.count_threshold_reached` is semantically correct for self-join hotspot counting. The `docs/reports/goal988_event_hotspot_scalar_threshold_profiler_2026-04-26.md` explicitly states this rationale: the application's hotspot rule (`neighbor_count_without_self >= HOTSPOT_THRESHOLD`) excludes the query point itself, while the underlying `fixed-radius threshold-count` primitive includes it. The `scripts/goal811_spatial_optix_summary_phase_profiler.py` correctly passes this adjusted threshold. The `examples/rtdl_event_hotspot_screening.py` further confirms this understanding by subtracting 1 from `neighbor_count` when generating hotspot rows in non-scalar modes.

2.  **Avoidance of Row Materialization for Compact Profiler Path**:
    Row materialization is effectively avoided for the compact profiler path. The `scripts/goal811_spatial_optix_summary_phase_profiler.py` in its `_run_event` function for `optix` mode directly calls `prepared.count_threshold_reached(...)`, which, as confirmed by `src/rtdsl/optix_runtime.py`, returns a single scalar integer (`threshold_reached_count.value`). This design bypasses the need to construct and return individual row dictionaries for each event, optimizing for a compact summary.

3.  **Honesty Regarding Non-Emission of Hotspot Identities**:
    The documentation is honest about hotspot identities not being emitted. The `docs/reports/goal988_event_hotspot_scalar_threshold_profiler_2026-04-26.md` clearly states that the profiler returns `hotspots: None` for this compact path. This is directly reflected in the `scripts/goal811_spatial_optix_summary_phase_profiler.py` implementation, which explicitly sets `"hotspots": None` in the `result` payload for the `event_hotspot_screening` scenario in `optix` mode.

4.  **Public RTX Speedup Claims Remain Unauthorized**:
    The documentation consistently and explicitly maintains that public RTX speedup claims remain unauthorized by this specific goal. `docs/reports/goal988_event_hotspot_scalar_threshold_profiler_2026-04-26.md` reiterates this multiple times. The `scripts/goal811_spatial_optix_summary_phase_profiler.py`'s `_cloud_claim_contract` sets `activation_status` to `"deferred_until_real_rtx_phase_run_and_review"`. The `docs/app_engine_support_matrix.md` entries for `event_hotspot_screening` also reinforce a bounded claim ("bounded prepared count-summary path may enter claim review; no whole-app hotspot-screening speedup claim") and a `deferred_until_real_rtx_phase_run_and_review` status for any public wording changes. The project's policy for requiring a fresh RTX artifact and independent review before any public wording changes is upheld.

**Summary:**

Goal988 successfully refactors the event-hotspot profiler to use a more efficient scalar threshold-count continuation, avoiding unnecessary row materialization. The implementation aligns perfectly with the stated design goals and respects existing policies regarding RTX speedup claims. The changes are semantically sound and the documentation accurately reflects the behavior.