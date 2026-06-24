# Call For Review: Phoenix V3 M5 Author-Code Recovery

Date: 2026-06-20

Reviewer: Claude or Gemini

## Scope

Please critically review the Phoenix V3 M5 update after recovering RayJoin
author `query_exec`.

This is V3-only work. Do not review V4 scope, C ABI, embedding, SDK packaging,
or external runtime interop as part of this packet.

## Files To Read

- `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_topology_intake_summary.json`
- `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620/m5_pip_point_location_parity_filtered_100k/summary.json`
- `docs/rebuild/v3/evidence/rayjoin_author_build_20260620/query_exec_build_compat.diff`
- `docs/rebuild/v3/v3_current_status_2026-06-20.md`
- `docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m1_m7_compliance_table_2026-06-20.md`
- `scripts/goal4373_rayjoin_cdb_point_location_compare.py`
- `scripts/v3_phoenix_m5_topology_intake.py`
- `tests/v3_phoenix_m5_topology_evidence_test.py`
- `tests/v3_phoenix_m5_topology_intake_test.py`

## Facts To Verify

- RayJoin author source was cloned from `https://github.com/rubaolee/RayJoin`
  at commit `02bf6220d6d20b04af77ee20364eced75cc029c9`.
- `query_exec` was rebuilt on the RTX 4000 Ada pod with CUDA 12.8 compatibility
  shims:
  - `src/util/markers.h`: `nvtx3/nvToolsExt.h`;
  - `src/CMakeLists.txt`: `ENABLED_ARCHS 89`;
  - PTX compile includes glog/gflags include paths.
- Final M5 intake:
  - `status=pass`;
  - `overall_status=internal_evidence_with_author_code`;
  - `m5_author_code_comparison_status=complete`;
  - `query_exec_status=present`;
  - `release_authorized=false`;
  - `public_speedup_claim_authorized=false`;
  - `phoenix_m7_qualified_release_rows=0`.
- PIP point-location final row:
  - backend-parity-filtered random bbox query CDB;
  - 100,000 accepted points;
  - 1 exact-row tie candidate rejected;
  - OptiX/Embree exact row mismatches: 0;
  - RayJoin author Query: 0.470400 ms;
  - RTDL OptiX median: 2.703801 ms;
  - RTDL Embree median: 5.214207 ms;
  - RTDL OptiX vs Embree: 1.928x;
  - OptiX native traversal vs Embree: 2.855x;
  - RayJoin author RT is 5.748x faster than RTDL OptiX.
- Overlay active-count remains an internal same-contract row, not full polygon
  overlay or RayJoin Section 5.7 reproduction.
- Tests run:
  - `py -3 -m unittest tests.v3_phoenix_m5_topology_evidence_test tests.v3_phoenix_m5_topology_intake_test tests.v3_rayjoin_pip_missing_author_test tests.v3_phoenix_m5_topology_packet_test`
    passed 12 tests.
  - `py -3 scripts/run_test_matrix.py --group v3_rebuild` passed 17 modules /
    60 tests.
  - `py -3 scripts/v3_release_wording_gate.py --pretty` passed.

## Review Questions

1. Is it correct to upgrade M5 from `internal-author-blocked` to
   `internal-author-complete`?
2. Does the evidence remain honest that RayJoin author RT beats RTDL OptiX on
   the PIP row?
3. Are the CUDA 12.8 compatibility shims sufficiently disclosed as external
   RayJoin build shims rather than RTDL algorithm changes?
4. Are release and public speedup claims still adequately blocked?
5. Is anything still misleading, missing, or too weak before this bounded M5
   author-recovery goal can be closed?

## Requested Output

Write a critical review to:

`docs/reviews/claude_phoenix_v3_m5_author_recovery_review_2026-06-20.md`

Use this verdict format:

- Verdict: approve / approve-with-required-fixes / request-changes
- P0/P1/P2 findings with file references
- Required fixes before bounded goal closure
- Notes on claim boundaries
