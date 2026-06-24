I now have all required inputs. Here is my external reviewer verdict.

---

## External Review: Phoenix V3 M61 Topology-Stream Gap Ledger
**Date:** 2026-06-23  
**Reviewer role:** external technical reviewer

---

### Verdict

```
accept_m61_gap_ledger_continue_local_m62
```

---

### Per-Question Findings

**Q1. Does M61 correctly label the 2.282x device-resident delta as internal, not public-row evidence?**

Yes. The label `internal_routing_delta_not_public_row` is applied consistently across all four artifacts (JSON root, internal_delta object, markdown, test assertions). The value is traced directly to `phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json` → `large_pip_device_resident_delta.device_resident_wall_speedup_vs_default = 2.2815293995139454`. Count parity (3,823,783) is verified. The ledger builder check `internal_delta_not_public_claim` gates all three downstream misuse vectors (`public_row_authorized`, `rtdl_beats_rayjoin_claim_authorized`, `true_zero_copy_claim_authorized`) as false simultaneously. The M3 gap JSON also preserves the "RayJoin author is still 11.5x faster than RTDL OptiX" finding, making the no-RTDL-beats-RayJoin rule data-backed, not just asserted.

**No issues.**

---

**Q2. Does M61 preserve the V3/V4 boundary and true-zero-copy prohibition?**

Yes, with layered enforcement:
- `true_zero_copy_claim_authorized: false` appears at the JSON root, in `internal_delta`, in the M50 runner dry-run and run paths, in `PreparedExecutionReport.__post_init__` (raises on authorization), and in the base `_execute_prepared_execution_session` metadata (line 475, `prepared_execution.py`).
- `external_device_buffer_interop_authorized = False` and `v4_embedding_or_external_zero_copy_authorized = False` are set in the `run_point_location_topology_stream_prepared_session` (lines 2199–2200) and `run_segment_intersection_topology_stream_prepared_session` (lines 2378–2379) functions specifically.
- The V3/V4 residency boundary text is present in multiple runner metadata blocks (`"RTDL-owned prepared structures and intermediates between RTDL phases are V3; exposing caller-owned device buffers to an external host remains V4"`).

**No issues.**

---

**Q3. Does M61 correctly record the phase-vocabulary gap between PreparedExecutionReport and the topology-stream M3 table?**

Yes, and this is the most substantively correct part of the packet. The two vocabularies are explicitly enumerated side-by-side:

- PreparedExecution: `prepare | cache_load | warmup | steady_state_stream | planner | executor | validation`
- Topology-stream M3: `static_scene_prepare_sec | query_stream_prepare_sec | device_transfer_or_residency_sec | rt_traversal_sec | topology_continuation_sec | host_return_or_scalar_materialization_sec`

These are semantically orthogonal — one is a session-lifecycle vocabulary, the other is a physical-phase timing vocabulary. `bridge_required: true` and `bridge_status: "must_map_or_supplement_prepared_execution_report_before_public_row"` are correct. The constraint that the bridge must attach as topology-stream-specific metadata rather than replace `PreparedExecutionReport` is the right architectural call. The test (`test_phase_bridge_records_prepared_report_to_m3_gap`) hard-codes all six M3 phase names to prevent drift.

**No issues.**

---

**Q4. Are the current topology-stream prepared-session surface checks meaningful?**

Partially. **P2 finding below.** The `current_surface` checks in `build_payload()` are string-presence checks against the raw text of `prepared_execution.py`. For example:

```python
"m3_phase_table_contract_metadata_present": (
    'metadata["topology_stream_m3_phase_table_contract"]' in prepared_source
)
```

This confirms the key is assigned somewhere in the file but does NOT verify:
- The assignment is inside the topology-stream runner functions (not another unrelated runner)
- The value assigned is the correct contract string (`topology_stream_m3_phase_table_contract_metadata_present` would be true even if the value were `None`)
- The M3 phase table emitted at runtime has non-null values for all six required phases

The checks confirm structural presence and are appropriate for a ledger/design stage where no run has occurred. They would be insufficient as release gates. For M62 the surface checks should be upgraded to at minimum import and call the runner with a stub dataset or verify the metadata values are the correct contract strings, not just that the key is assigned.

**P2 — surface checks are text-mining, adequate for a no-run ledger stage but must be tightened before any run-gated step.**

---

**Q5. Are the M50 fail-closed checks sufficient for this local ledger stage?**

Yes. The M50 runner is well-constructed:
- Dry-run by default: `if not bool(args.execute)` returns immediately without importing or calling `rayjoin_app`
- Authorization token required: exact string match `"M50_SPATIAL_TOPOLOGY_STREAM_M3_POD_AUTHORIZED"` is checked; mismatch raises `SystemExit` before any execution
- All public claim flags are false in both the dry-run and run-path payloads
- `validate_sample()` inside the run path would reject any sample that set an authorization flag true

The ledger checks all four of these via string presence, which is correct for verifying the gate structure exists. No execution is triggered by building the ledger.

**No issues.**

---

**Q6. Is M62 correctly limited to local contract/gate implementation, with no POD or public claims?**

Yes. The `m61_next_contract.m61_must_not_do` list is machine-readable and covers the critical prohibition surface: no M50 run, no public speedup from the 2.282x delta, no RTDL-beats-RayJoin, no true-zero-copy labeling, no RayJoin-specific shortcuts. The report and call-for-review both state "No execution run is authorized by M61." The test `test_m61_ledger_is_local_no_pod_not_release` will fail the ledger if `release_authorized`, `all_app_benchmark_authorized`, `paid_pod_spend_authorized`, `focused_pod_spend_authorized`, `public_speedup_claim_authorized`, `rtdl_beats_rayjoin_claim_authorized`, `true_zero_copy_claim_authorized`, or `v4_work_authorized` become true.

One minor observation: the packet refers to M62 for the next allowed step but `m61_next_contract` is titled as M61's forward scope. This is consistent with the milestone numbering convention (M61 produces the ledger; M62 implements/gates) but could confuse a reader. Not blocking.

**No issues.**

---

**Q7. Does the packet preserve all non-authorization boundaries?**

Yes, exhaustively. The JSON root contains 14 explicit `*_authorized: false` fields. The markdown non-authorization block lists all 14 prohibited items verbatim. The test `test_report_and_review_packet_preserve_boundaries` verifies all key prohibition strings appear in both REPORT and CALL_FOR_REVIEW, and additionally asserts `"release_ready"` does NOT appear in either file. Every layer is consistent.

**No issues.**

---

### Findings Summary

**P0 (blocking):** None.

**P1 (significant):** None.

**P2 (note for M62):**

1. **Surface checks are text-mining, not behavioral.** The `current_surface` checks confirm string literals appear in `prepared_execution.py` but do not verify the topology-stream runner functions assign correct contract values at runtime. Before M62 produces a run-gated artifact, these checks should verify the actual assigned values (e.g., import the constant `TOPOLOGY_STREAM_M3_PHASE_TABLE_CONTRACT` and assert it equals the expected string in a test, or run the runner with a mock input and inspect the metadata).

2. **`true_zero_copy_claim_authorized` is not explicitly set inside the topology-stream runner metadata blocks** (lines 2168–2215 and 2347–2395 in `prepared_execution.py`). It is inherited from the base `_execute_prepared_execution_session` metadata at line 475. The `no_true_zero_copy_claim` surface check would pass even if the topology-stream runner code were restructured to not call the base runner. This is not a current gap but is a fragility to fix in M62 by adding the explicit assignment.

3. **The delta lower-bound test (`assertGreater(delta["wall_speedup_vs_default"], 2.0)`) has no upper bound.** A data corruption that produced a wildly wrong speedup (e.g., 200x) would pass the test. Not critical at this stage but consider adding a sanity cap.

---

### Non-Authorization Confirmation

This review does **not** authorize: V3 release, all-app benchmark, paid POD spend, focused POD spend, public speedup wording, broad V3-over-V2 claim, whole-app speedup claim, paper reproduction claim, RTDL-beats-RayJoin claim, V4 work, embedding, C ABI, true-zero-copy claim, or watch-row closure.
