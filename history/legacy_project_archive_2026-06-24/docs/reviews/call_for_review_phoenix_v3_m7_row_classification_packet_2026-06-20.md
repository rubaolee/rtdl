# Call For Review: Phoenix V3 M7 Row Classification Packet

Date: 2026-06-20

Requested reviewer: Claude

## Scope

Review the Phoenix V3 M7 row classification packet and its gates.

Primary files:

```text
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json
scripts/v3_phoenix_m7_row_classification_packet.py
tests/v3_phoenix_m7_row_classification_packet_test.py
scripts/v3_release_wording_gate.py
scripts/run_test_matrix.py
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md
docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md
docs/rebuild/v3/README.md
```

Relevant source evidence:

```text
docs/rebuild/v3/phoenix_v3_p0_route_capability_map_2026-06-20.json
docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json
docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_topology_intake_summary.json
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.json
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_524288.json
docs/rebuild/v3/evidence/phoenix_v3_triangle_prepared_graph_20260620/triangle_prepared_graph_intake_summary.json
docs/rebuild/v3/evidence/phoenix_v3_rtnn_ranked_summary_20260620/rtnn_ranked_summary_intake_summary.json
```

Verification already run by Codex:

```text
py -3 -m unittest tests.v3_phoenix_m7_row_classification_packet_test tests.v3_phoenix_route_capability_map_test tests.v3_release_wording_gate_test
13 tests OK

py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
release_authorized: false
public_speedup_claim_authorized: false

py -3 scripts/run_test_matrix.py --group v3_rebuild
23 modules / 87 tests OK
```

## Review Questions

1. Is the M7 packet too permissive anywhere? It should not authorize V3 release, public speedup wording, broad V3-over-V2 wording, paper reproduction, or whole-app speedup.
2. Does it preserve the hard negative facts:
   - M4 M10 accounting warning and system Python packaging gap;
   - M5 RayJoin author RT faster than RTDL OptiX;
   - M6 fused Numba CUDA fastest and prepared OptiX slower;
   - RayDB hot-query-only and 213s+ setup/cold cost for sum;
   - Triangle synthetic/non-paper boundary;
   - RTNN hot rows win but wall timing regresses?
3. Are the tests and wording gate strong enough to prevent regression?
4. Is the row map correctly strict with zero M7-qualified release rows?
5. What P0/P1 fixes are required before Codex writes 2-AI consensus for this bounded packet?

## Required Output

Please save your review to:

```text
docs/reviews/claude_phoenix_v3_m7_row_classification_packet_review_2026-06-20.md
```

Use a concrete verdict:

```text
approve
approve-with-required-fixes
reject
```

List P0 and P1 issues separately. If there are no P0 issues, say that clearly.
