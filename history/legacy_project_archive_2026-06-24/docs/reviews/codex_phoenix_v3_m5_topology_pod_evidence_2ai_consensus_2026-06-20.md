# Codex 2-AI Consensus: Phoenix V3 M5 Topology Pod Evidence

Date: 2026-06-20

Scope: close the Phoenix V3 M5 topology evidence cycle as internal evidence,
not release evidence.

## External Review

Claude review:

`docs/reviews/claude_phoenix_v3_m5_topology_pod_evidence_review_2026-06-20.md`

Verdict: approve with amendments.

Claude P0/P1 findings:

- P0: none blocking internal use.
- P1: retire the misleading `safe100k` artifact name.
- P1: tighten M5 status away from `partial-plus` to an author-code-blocked
  label.
- P1: give the `query_exec` blocker a concrete owner/next action.

## Amendments Applied

- Current accepted artifact directory is now
  `m5_pip_point_location_parity_filtered_100k`.
- Query CDB is now named
  `goal4373_query_points_parity_filtered_100k.cdb`.
- `summary.json` records:
  - `artifact_methodology_label: parity_filtered_100k`;
  - `legacy_safe100k_name_retired: true`;
  - a reason explaining the retired name.
- `METHODOLOGY_NOTE.md` explains that the old `safe100k` label is retired and
  the accepted stream is backend-parity filtered.
- Packet, remote run script, intake script, and tests all use the new
  parity-filtered path.
- M1-M7 status now labels M5 as `internal-author-blocked`, not `partial-plus`.
- The release blocker table names the Phoenix V3 rebuild owner and next action:
  locate or rebuild RayJoin author `query_exec`, rerun the author-code arm plus
  intake, then review into M7 or keep internal.

## Evidence Accepted

Internal M5 topology evidence passed:

- GPU/env gates passed on NVIDIA RTX 4000 Ada Generation.
- PIP point-location:
  - 100,000 parity-filtered points;
  - 1 exact-row tie candidate rejected before timing;
  - 0 exact `(point_id, face_id, segment_id)` mismatches after filtering;
  - OptiX and Embree positive-face count: 43,738;
  - internal RTDL OptiX/Embree ratio: 1.870x;
  - internal native traversal ratio: 2.764x.
- Overlay active-count:
  - active count: 174;
  - same output contract: `overlay_active_pair_dependency_count`;
  - OptiX/Embree active counts match;
  - row materialization avoided;
  - internal Embree/OptiX timed median ratio: 499.112x.

Release boundaries:

```text
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
m5_author_code_comparison_status: blocked_query_exec_missing
status_label: internal-author-blocked
```

## Verification

```text
py -3 -m unittest tests.v3_phoenix_m5_topology_evidence_test tests.v3_phoenix_m5_topology_packet_test tests.v3_phoenix_m5_topology_intake_test tests.v3_release_wording_gate_test
11 tests OK

py -3 scripts\run_test_matrix.py --group v3_rebuild
17 modules, 59 tests OK

py -3 scripts\v3_release_wording_gate.py --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.md --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.json --require-scanned docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md --pretty
status: pass
missing_required_scanned_files: []
violations: []
```

## Consensus

Codex agrees with Claude: this M5 cycle is approved for internal engineering
evidence after amendments, but it cannot close M5 author-code comparison and
cannot feed release/public speedup wording.

Decision: M5 evidence cycle closed as `internal-author-blocked`.

Next M5 action: locate or rebuild RayJoin author `query_exec` and rerun the
author-code arm plus intake.

## Goal-Level Decision Audit

Decision: close this bounded M5 evidence cycle as internal-author-blocked.

1. Was I foolish?

   Yes, earlier in the cycle. I used an unbounded `query_exec` search and kept
   stale `safe100k` naming after discovering tie sensitivity.

2. What actions made the decision foolish?

   The unbounded `/workspace /root` find wasted pod time, and the old name could
   have let future readers mistake filtered evidence for an unfiltered safe
   stream.

3. Was there another path?

   Yes. The correct path was bounded preflight, backend-parity filtering, and a
   status label that foregrounds the missing author binary.

4. Can I now try a different path that actually solves the problem?

   Yes. The current M5 evidence is now honest and tested. The next solving path
   is the author-code recovery/rebuild step, not more reinterpretation of the
   current partial evidence.
