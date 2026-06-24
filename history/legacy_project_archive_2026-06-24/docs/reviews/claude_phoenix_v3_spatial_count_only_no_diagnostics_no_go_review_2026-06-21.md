# Claude External Review: Phoenix V3 Spatial Count-Only/No-Diagnostics No-Go

**Reviewer:** Claude Code (claude-sonnet-4-6)
**Date:** 2026-06-21
**Verdict:** `accept`

---

## Review Scope

This review assesses whether the no-go decision for the
`RTDL_OPTIX_RELATION_STATUS_CORRECTED_COUNT_ONLY_NO_DIAGNOSTICS` experimental
flag is evidence-supported, whether the flag was correctly removed from source,
and whether release/M7/public claims remain false in docs and gates.

Evidence read:

- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.json`
- `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_count_only_no_diag_20260621/diagnostic_prefilter_zero_repeat50_sample7.json`
- `docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_count_only_no_diag_20260621/count_only_prefilter_zero_repeat50_sample7.json`
- `docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`
- `scripts/v3_phoenix_spatial_relation_status_count_only_no_diagnostics_no_go.py`
- `tests/v3_phoenix_spatial_relation_status_count_only_no_diagnostics_no_go_test.py`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `src/native/optix/rtdl_optix_workloads.cpp` (flag search)

---

## Decision Under Review

Remove the count-only/no-diagnostics code path from source after a repeat50/sample7
paired test on `br_county.cdb` showed it was slower than the diagnostic baseline
despite preserving the exact count.

---

## Finding 1: No-Go Decision Is Evidence-Supported

**Assessment: Supported.**

The raw data is consistent and directionally unambiguous. Across all 7 samples, the
count-only/no-diagnostics `prepared_query_sec` is higher than the diagnostic
`prepared_query_sec` in every individual sample:

| Sample | Diagnostic (ms) | Count-only (ms) | Delta (ms) |
|--------|----------------|----------------|------------|
| 0 | 2.034035 (sample 0 cold) | 2.035141 (sample 0 cold) | +0.001106 |
| 1 | 1.897592 | 1.902517 | +0.004925 |
| 2 | 1.894128 | 1.903873 | +0.009745 |
| 3 | 1.898780 | 1.903840 | +0.005060 |
| 4 | 1.894940 | 1.904737 | +0.009797 |
| 5 | 1.893662 | 1.903441 | +0.009779 |
| 6 | 1.903057 | 1.904961 | +0.001904 |

Median delta: **+0.006281 ms** (count-only is slower). The margin is small (~0.33%
relative) but the *direction is consistent across all 7 samples* — no sample has
count-only faster. This rules out noise as the cause and makes the no-go
decision sound.

The RT-traversal (native `candidate_count_pass`) also shows count-only slower in
the median (1.863252 ms vs 1.855051 ms, delta +0.008201 ms), corroborating the
prepared-query result at the kernel level.

Both candidates remain slower than the 1.865660 ms RayJoin author Query bar
(count-only gap: +0.038213 ms; diagnostic gap: +0.031932 ms). The no-go is
therefore correct: the candidate neither improves performance nor clears the
author bar.

**Why the count-only path might be slower**: Suppressing diagnostic atomics
changes the compiled kernel code path in a way that does not benefit the hot
loop. This is plausible given GPU code-generation behavior with conditional
write suppression. The review does not require an explanation — the data is
sufficient for rejection.

---

## Finding 2: Failed Flag Removed From Source

**Assessment: Verified.**

Live grep of `src/native/optix/rtdl_optix_workloads.cpp` for
`RTDL_OPTIX_RELATION_STATUS_CORRECTED_COUNT_ONLY_NO_DIAGNOSTICS`: **zero matches**.

The surviving prefilter-zero flag `RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO`
is present at line 8765 of the same file, which is correct — the near-miss
optimization is retained while the no-go variant is removed.

The script (`v3_phoenix_spatial_relation_status_count_only_no_diagnostics_no_go.py`)
reads the source file live at packet-build time and checks `COUNT_ONLY_FLAG not
in source_text` as a hard gate check (`native_source_does_not_keep_failed_count_only_flag`).
The test (`test_failed_flag_is_not_retained_in_native_source`) asserts the same
condition from the live source file at test execution time. Both checks pass per
the committed packet's `"failed_checks": []`.

---

## Finding 3: Release, M7, and Public Claims Remain False

**Assessment: Correct across all layers.**

**Evidence packets**: Both `diagnostic_prefilter_zero_repeat50_sample7.json` and
`count_only_prefilter_zero_repeat50_sample7.json` carry `release_authorized: false`,
`m7_promotion_authorized: false`, `public_speedup_claim_authorized: false`,
`rtdl_beats_rayjoin_claim_authorized: false`, `broad_v3_faster_than_v2_claim_authorized:
false`, and `true_zero_copy_claim_authorized: false`. Both show
`"m7_rows_added": 0` and `"m7_qualified_release_rows_added": 0`.

**No-go packet**: All 16 claim flags are `false`. Status is
`spatial_relation_status_count_only_no_diagnostics_no_go_not_m7`. Zero M7 rows added.

**Release readiness gate** (`v3_phoenix_release_readiness_gate.py`): `release_authorized`
is hardcoded `False` with no code path to `True`. Four explicit blocking reasons:
`release_authorization_false`, `twelve_row_surface_still_too_narrow_for_major_release`,
`missing_point_location_topology_stream_m7_capability_family`,
`twelve_row_release_readiness_consensus_blocks_release`.

**Work queue** (`phoenix_v3_next_generic_engine_work_queue_2026-06-21.md`): The
`spatial_rayjoin_topology_stream_author_gap` section correctly records the
count-only no-go with status `spatial_relation_status_count_only_no_diagnostics_no_go_not_m7`,
prepared-query 1.903873 ms, delta +0.006281 ms, and `source retained: false`.
The item is under `Future Research Records`, not the active queue. The gate
script requires 40+ verbatim phrases from this document and will fail if these
entries are removed or altered.

The `RTDL-beats-RayJoin` and broad V3-over-V2 claims remain forbidden. The
`existing_evidence_promotable_now: false` assertion in the gate blocks any
attempt to promote this evidence to a release row.

---

## P0 Issues

**None.**

The no-go is evidence-supported, the flag is absent from source, and the claim
boundaries are enforced at all layers (packet, gate, work queue, test).

---

## P1 Issues

**P1-1**: `git_commit: null` in both evidence packet `environment` blocks.

Both `diagnostic_prefilter_zero_repeat50_sample7.json` and
`count_only_prefilter_zero_repeat50_sample7.json` record `"git_commit": null`.
The GPU identity (`NVIDIA RTX 4000 Ada Generation, 550.127.05`) and POD host
(`213.173.108.14:11592`) are present, but the source commit hash at measurement
time is not captured. For a no-go experiment that led to source deletion, this
is a minor provenance gap — a reviewer cannot independently confirm which source
revision was measured. The test asserts the flag is absent from the *current*
source at test time, which partially compensates, but does not reconstruct the
exact measured state. Recommend capturing `git rev-parse HEAD` in evidence
packets going forward.

---

## Engineering Judgment on Removing the Flag

Removing a default-off flag that slowed the kernel and preserved nothing useful
is the correct call. Keeping it as dead code with a comment ("slower, but
preserved for reference") would increase maintenance surface for zero benefit.
The work queue document and the no-go packet provide the permanent record that
the idea was tried and rejected — the source should not carry that burden.

---

## Summary

| Question | Answer |
|----------|--------|
| Is the no-go evidence-supported? | Yes — slower in all 7 samples, consistent direction |
| Is removing the flag the right call? | Yes — confirmed absent from source |
| Do release/M7/public claims remain false? | Yes — enforced at packet, gate, queue, and test layers |
| P0 issues? | None |
| P1 issues? | P1-1: no git commit hash in evidence packets |

**Verdict: `accept`**

The no-go decision is correctly made, correctly recorded, and correctly enforced.
The prefilter-zero near-miss remains the surviving candidate at 1.903493 ms,
still 0.037833 ms above the 1.865660 ms author bar. Spatial topology-stream
remains `future_research_not_current_p0`. This review does not authorize release,
M7 promotion, or any public claim.
