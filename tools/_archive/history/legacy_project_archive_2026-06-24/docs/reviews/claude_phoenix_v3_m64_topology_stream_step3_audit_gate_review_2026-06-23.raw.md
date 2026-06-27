I have read all required files. Here is the formal recorded review.

---

## Critical Review: Phoenix V3 M64 Topology-Stream Step3 Audit Gate

**Review date:** 2026-06-23
**Reviewer:** Claude (Sonnet 4.6), via session-level code review
**Files reviewed:**
- `docs/reviews/call_for_review_phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md`
- `docs/reports/phoenix_v3_m64_topology_stream_step3_audit_gate_2026-06-23.md`
- `src/rtdsl/prepared_execution.py` (full, via paged read + targeted grep)
- `tests/v3_phoenix_prepared_execution_session_runner_test.py` (full, paged)
- `tests/v3_phoenix_spatial_segment_intersection_runner_wiring_test.py` (full)
- `docs/rebuild/v3/phoenix_v3_m61_topology_stream_gap_ledger_2026-06-23.json`

---

### 1. Does M64 correctly restrict the Step3 bridge requirement to topology-stream Set-A candidates?

**Yes.** The detection logic in `audit_prepared_execution_session_metadata` (line 3378):

```python
topology_stream_set_a_candidate = (
    set_a_probe_candidate and "topology_stream" in primitive_family
)
```

...and the bridge-readiness guard (line 3405):

```python
topology_stream_m3_bridge_ready = (
    not topology_stream_set_a_candidate
    or (
        topology_stream_m3_bridge_contract_ok
        and topology_stream_m3_bridge_complete
        and topology_stream_m3_bridge_non_authorizing
    )
)
```

The `not topology_stream_set_a_candidate` arm is the correct short-circuit. Set-B runners (`set_a_probe_candidate=False`) hit it immediately. Set-A non-topology-stream runners (`primitive_family` without `"topology_stream"`) also hit it. Only runners that are both `set_a_probe_candidate==True` **and** contain `"topology_stream"` in `primitive_family` reach the bridge check. The test at line 1124 of the session-runner test confirms `fixed_radius_threshold_reached_count_2d` still yields `accept_step3_ready` without a bridge, and the AABB Set-B tests confirm the same for Set-B. **No collateral damage observed.**

---

### 2. Are the required bridge fields sufficient?

**Yes, for the declared purpose.** The six logical conditions that must all be true for a topology-stream candidate to pass:

| Condition | Field checked |
|---|---|
| Contract name is canonical | `prepared_execution_to_topology_stream_m3_bridge_contract == "prepared_execution_to_topology_stream_m3_bridge_v1"` |
| Bridge status is complete | `prepared_execution_to_topology_stream_m3_bridge_status == "complete_non_authorizing_m3_bridge"` |
| Phase table is fully populated | `topology_stream_m3_phase_table_complete is True` |
| No missing public-row phases | `topology_stream_m3_missing_phases_for_public_row == ()` |
| No public-row authorization | `topology_stream_m3_bridge_public_row_authorized is False` |
| No M7 promotion authorization | `topology_stream_m3_bridge_m7_promotion_authorized is False` |

A runner with a missing or partial M3 table will fail condition 3 and/or 4. A runner with the wrong contract string or status fails conditions 1 or 2. The non-authorizing check (conditions 5–6) is strict: `None is False` evaluates to `False`, so absent fields also fail, which is correct conservative behavior.

**One observation for M65 (not a blocking defect):** The non-authorizing check treats a missing `topology_stream_m3_bridge_public_row_authorized` field as "not non-authorizing" (bridge fails). This is the right conservative default but could surprise a future caller who omits the field by mistake. A descriptive error message or field-presence assertion in the runner helpers would improve diagnostics.

---

### 3. Does the negative test prove broken bridge metadata becomes `incomplete_step3_audit`?

**Yes.** In `test_point_location_topology_stream_helper_routes_generic_family_through_runner` (line 862), the inline negative test:

1. Takes the passing `metadata` (which produces `accept_step3_ready`)
2. Mutates `topology_stream_m3_phase_table_complete = False` and sets `topology_stream_m3_missing_phases_for_public_row = ("topology_continuation_sec",)`
3. Asserts `broken_audit["status"] == "incomplete_step3_audit"`
4. Asserts `broken_audit["topology_stream_m3_bridge_ready"] is False`
5. Asserts `"complete_non_authorizing_topology_stream_m3_bridge"` appears in `missing_step3_fields`

This concretely proves the mechanism. The segment-intersection wiring test does not have an explicit negative path, but the positive path in that test verifies all four bridge fields (lines 174–177), which is consistent with the bridge requirement applying to both topology-stream families.

**One observation for M65 (not a blocking defect):** The negative test exercises only the `phase_table_complete=False` + `missing_phases` failure mode. The `bridge_contract` mismatch and `bridge_status` mismatch paths, and the `public_row_authorized=True` path, are not independently tested. These are not required for M64 acceptance but should be added before Step-3 → Step-4 handoff.

---

### 4. Are non-authorization boundaries preserved?

**Yes, at three independent layers:**

**Layer 1 — Audit return is hardcoded.** The return dict of `audit_prepared_execution_session_metadata` (lines 3478–3483) unconditionally sets `release_authorized: False`, `public_speedup_claim_authorized: False`, `broad_v3_faster_than_v2_claim_authorized: False`, `true_zero_copy_claim_authorized: False`, `v4_embedding_or_external_zero_copy_authorized: False`. The audit function cannot produce True for any of these fields regardless of input.

**Layer 2 — `claim_boundaries_closed` check in incoming metadata.** Lines 3413–3420 check five fields in the incoming metadata; if any is True, `claim_boundaries_closed=False` → `step3_ready=False` → `incomplete_step3_audit`. This means a runner that accidentally sets a claim field True will be caught.

**Layer 3 — Bridge non-authorizing check.** Lines 3401–3404 independently verify that neither `topology_stream_m3_bridge_public_row_authorized` nor `topology_stream_m3_bridge_m7_promotion_authorized` is True. This is an additional topology-stream-specific authorization gate.

The `PreparedExecutionReport.__post_init__` at line 120 also enforces that all boolean authorization fields in the report object itself must be False. Authorization boundaries are consistently enforced from construction through audit.

---

### 5. May local Phoenix V3 Step-2/Step3 topology-stream work continue after M64?

**Yes.** M64 is fully local Step-3 audit work. It:
- Does not run POD
- Does not make public claims
- Does not benchmark all-app or authorize any measurement claims
- Tests pass (43 session/wiring tests + 15 ledger/M62/M63 gate tests)
- The gap ledger shows `failed_checks: []`
- The bridge gate is now mandatory for topology-stream Step3, blocking the previously possible false-positive where `runtime_trunk_executes_end_to_end=True` could bypass a missing M3 table

M64 completes its stated job: making the M63 bridge machine-enforceable inside Step3. Step-2/Step3 topology-stream work is what M65 would continue, and M64 does not block that.

---

### 6. What smallest fixes, if any, are required before M65?

**No blocking defects found.** The following are observations only, appropriate for M65's own scope:

| Item | Severity | Suggested M65 action |
|---|---|---|
| Negative test covers only `phase_table_complete=False`. Bridge contract mismatch, status mismatch, and `public_row_authorized=True` paths are untested. | Low | Add 2–3 additional negative sub-tests |
| Missing `topology_stream_m3_bridge_public_row_authorized` field fails silently (bridge fails with no message explaining which field is absent) | Low | Add field-presence assertion or descriptive missing-field entry |
| Segment-intersection wiring test has no inline negative path (positive path only verifies bridge is present) | Low | Optionally mirror the point-location negative inline test |

None of these require fixes before M65 starts.

---

### Verdict

```
accept_m64_topology_stream_step3_audit_gate_continue_local_step2_no_pod_no_release
```

M64 is correctly scoped, mechanically sound, and causally connected to M63. The bridge-mandatory gate fires only on topology-stream Set-A candidates, non-topology runners are untouched, the negative test proves a broken bridge blocks Step3, and all authorization boundaries are hardcoded False in the audit return.

---

### Explicit Non-Authorization Statement

This review verdict **does not authorize and explicitly excludes**:

- V3 release
- All-app benchmark run
- Paid POD spend
- Focused POD spend
- Public speedup wording
- Broad V3-over-V2 claim
- Whole-app speedup claim
- Paper reproduction claim
- RTDL-beats-RayJoin claim
- True-zero-copy claim
- V4 work
- Embedding
- C ABI
- Watch-row closure

Local Phoenix V3 Step-2/Step3 topology-stream work (no POD, no release) may continue.
