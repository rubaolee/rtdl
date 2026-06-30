# Independent Review: Goal3517 Prepared Execution Pattern

Reviewer: Claude (independent)
Date: 2026-06-05
Source report: `docs/reports/goal3517_prepared_execution_user_pattern_2026-06-05.md`
Verdict: `accept-with-boundary`

---

## Findings

### Finding 1 (minor / cosmetic): `PREPARED_EXECUTION_CLAIM_BOUNDARY` text is incomplete

The constant text in `src/rtdsl/prepared_execution.py` lines 28–34 names:
> "release, public speedup wording, broad RT-core speedup wording, true zero-copy wording,
> paper-reproduction wording, hidden partner selection, or app-specific native-engine behavior"

The source artifact's `claim_boundary` dict also carries `full_overlay_area_claim_authorized`,
`rayjoin_paper_reproduction_claim_authorized`, and `rtdl_beats_rayjoin_claim_authorized`. These
are validated against the inherited dict and refused if `True`, so no enforcement gap exists.
The boundary text could name them explicitly for consistency with the artifact schema; this is
cosmetic, not structural.

### Finding 2 (informational): Backend inference fallback is a placeholder, not a live inference

`_infer_backend_from_artifact` at lines 346–352 returns `"explicit_backend_not_recorded"` if
neither `"optix"` appears in the schema nor `"gpu"` in the artifact. This is correct defensive
behavior. Callers who pass `backend="optix"` explicitly (as the test and script both do) bypass
this path entirely. No action required.

### Finding 3 (informational): Tests could not be executed locally

The PowerShell sandbox blocked the test run. Code inspection confirms all four test cases
match the implementation: the partner-is-explicit test exercises `describe_prepared_execution_user_pattern`,
the normalization test reads the live Goal3511 artifact and checks all required phases plus
timing values, the runner-wiring test checks the script for the required phrases, and the
rejection test covers both a missing-phase and an over-authorized payload. No logic gap found.

---

## Review Questions

### Q1. Does Goal3517 correctly define the workflow `prepare -> pack/cache -> warm -> run steady-state -> explain timings`?

Yes. `PREPARED_EXECUTION_WORKFLOW` in `prepared_execution.py:12–18` is:

```python
("prepare", "pack_or_cache", "warm", "run_steady_state", "explain_timings")
```

`describe_prepared_execution_user_pattern()` returns this tuple verbatim (line 159), and the
test at `test_public_pattern_is_explicit_and_non_authorizing` asserts exact equality.

### Q2. Does the helper expose setup time, cache load/write time, warmup count, steady-state relation stream time, planner time, executor time, and validation time without collapsing them into one number?

Yes. `prepared_execution_report_from_artifact` constructs nine distinct
`PreparedExecutionPhaseTiming` objects:

| Phase | Source key | Candidate flag |
| --- | --- | --- |
| `prepare` | `timing_sec.geometry_plus_payload_prepare` | setup |
| `cache_load` | `timing_sec.payload_cache_load` | setup |
| `cache_write` | `timing_sec.payload_cache_write` | setup |
| `warmup` | `timing_sec.active_relation_device_columns_warmup_secs` (full repeat list) | setup |
| `steady_state_stream` | `timing_sec.active_relation_device_columns` | steady_state |
| `candidate_filter` | `timing_sec.bounds_positive_filter` | steady_state |
| `planner` | best of `device_tile_task_planning_best_repeat` / `device_tile_task_planning` | steady_state |
| `executor` | best of `cupy_tile_task_executor_best_repeat` / `cupy_tile_task_executor` | steady_state |
| `validation` | `timing_sec.exact_oracle` | validation |

`warmup_count` is recorded separately in `PreparedExecutionReport`. The `summary_sec` dict
aggregates into three buckets (setup / steady_state / validation) but all nine individual
phase timings remain accessible in `phase_timings`. Nothing is collapsed.

Warmup keeps all repeat seconds: the Goal3511 artifact yields
`[0.3716, 0.0075, 0.0072]` in `repeat_seconds` and
`min(warmup_seconds) = 0.0072` as the primary warmup value.

### Q3. Does it keep partner/backend choice explicit and avoid automatic partner selection?

Yes. `PreparedExecutionReport` requires non-empty `explicit_backend` and `explicit_partner`
(enforced in `__post_init__`, lines 86–98). The `automatic_partner_selection_allowed` field
defaults `False` and is rejected if `True` by both `__post_init__` (line 107) and
`validate_prepared_execution_report` (line 312). The serialized dict always emits
`"explicit_partner_choice_required": True` (line 133).

The partner-resolution fallback at line 192 prefers the caller-supplied `partner` argument,
then `executor_metadata.partner`, then `artifact.partner`, and finally
`"explicit_partner_not_recorded"` — an opaque placeholder, not a live selection. In the
overlay-area artifact the partner is `"cupy"` from `executor_metadata.partner`.

### Q4. Does it preserve all claim boundaries: no release, public speedup, broad RT-core speedup, true zero-copy, RayJoin reproduction, `rtdl beats RayJoin`, full overlay, hidden dispatch, or app-specific native-engine claims?

Yes, with the cosmetic gap noted in Finding 1. Enforcement is two-layered:

**Layer 1 — named flags on `PreparedExecutionReport`:**
`release_authorized`, `public_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`,
`true_zero_copy_claim_authorized`, `app_specific_engine_logic_allowed`, and
`automatic_partner_selection_allowed` all default `False` and raise `ValueError` if `True`
(lines 99–111). `validate_prepared_execution_report` independently rejects any that are not
`False` (lines 307–316).

**Layer 2 — inherited source `claim_boundary` dict:**
`_source_claim_boundary` copies all key/value pairs from the artifact's `claim_boundary` dict.
`__post_init__` rejects any that are truthy (lines 109–111). `validate_prepared_execution_report`
does the same (lines 317–319). The Goal3511 artifact carries seven boundary flags, all `False`:
`full_overlay_area_claim_authorized`, `public_speedup_claim_authorized`,
`rayjoin_paper_reproduction_claim_authorized`, `release_authorized`,
`rt_core_speedup_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`,
`true_zero_copy_claim_authorized`.

`"hidden dispatch"` is addressed implicitly: `explicit_partner_choice_required: True` and
`automatic_partner_selection_allowed: False` together prevent hidden dispatch.

### Q5. Is it acceptable that no new pod run was performed?

Yes. Goal3517 is a reporting-contract and documentation normalization goal. It consumes the
existing Goal3511 pod artifact unchanged and does not alter any measured execution path.
The test directly reads the Goal3511 artifact and verifies that the normalization round-trips
correctly; this is the appropriate validation scope for a documentation cleanup goal.

A fresh pod artifact is appropriate in a future goal (the self-report names Goal3521) that
needs current-HEAD confirmation with the `prepared_execution_report` field included inline.

---

## Verdict

`accept-with-boundary`

Goal3517 correctly defines the five-step workflow, exposes all required phase timings without
collapsing them, keeps partner and backend explicit with machine-enforceable guards, inherits
and re-validates all source claim boundary flags, and correctly defers a new pod run to a
successor goal. The cosmetic gap in `PREPARED_EXECUTION_CLAIM_BOUNDARY` text (Finding 1) does
not weaken enforcement; it is noted for a future text update but does not block acceptance.
