# Codex 2-AI Consensus: Phoenix V3 M5 Author-Code Recovery

Date: 2026-06-20

Status: bounded goal closed as internal author-code-complete evidence.

## Reviewed Artifacts

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m5_author_recovery_2026-06-20.md`
- External Claude review:
  `docs/reviews/claude_phoenix_v3_m5_author_recovery_review_2026-06-20.md`
- Current evidence report:
  `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md`
- Current evidence artifact:
  `docs/rebuild/v3/evidence/phoenix_v3_m5_topology_20260620`
- RayJoin author build evidence:
  `docs/rebuild/v3/evidence/rayjoin_author_build_20260620`

## External Review Verdict

Claude verdict: `approve-with-required-fixes`.

Claude found no P0 blockers and explicitly said the bounded M5 author-recovery
goal can be closed. Claude accepted the upgrade from `internal-author-blocked`
to `internal-author-complete`, with M7-before-promotion fixes around wording,
timing methodology, and generic capability tagging.

## Actions Taken After Review

- Replaced the risky generated wording that said the row "supports the paper's
  PIP claim."
- Added `comparison_methodology.timing_basis_note` to the PIP summary and M5
  intake output.
- Added `rayjoin_rt_speedup_vs_rtdl_optix_native_traversal` to the PIP
  comparison output.
- Added `generic_capability: point_location_topology_stream` to the intake
  summary.
- Added `status_label: internal-author-complete` to the intake summary.
- Added `overlay_author_comparison_status:
  not_applicable_internal_same_contract_only` to the intake summary.
- Re-ran the M5 PIP author comparison on the RTX 4000 Ada pod after these
  fixes and copied the artifact back locally.

## Final Evidence Facts

Final M5 intake:

```text
status: pass
overall_status: internal_evidence_with_author_code
status_label: internal-author-complete
generic_capability: point_location_topology_stream
m5_author_code_comparison_status: complete
query_exec_status: present
overlay_author_comparison_status: not_applicable_internal_same_contract_only
release_authorized: false
public_speedup_claim_authorized: false
phoenix_m7_qualified_release_rows: 0
```

Final PIP row:

```text
RayJoin author Query: 0.470115 ms
RTDL OptiX wall median: 2.692629 ms
RTDL OptiX native traversal median: 1.814979 ms
RTDL Embree wall median: 5.169664 ms
RTDL Embree native traversal median: 5.143595 ms
RTDL OptiX vs Embree wall ratio: 1.920x
RTDL OptiX vs Embree native traversal ratio: 2.834x
RayJoin author vs RTDL OptiX wall-vs-Query ratio: 5.728x
RayJoin author vs RTDL OptiX native traversal ratio: 3.861x
```

This is not an `RTDL beats RayJoin` result. RayJoin author RT is faster than
RTDL OptiX on this same-contract PIP row.

## Verification

Passed:

```text
py -3 -m unittest tests.v3_phoenix_m5_topology_evidence_test tests.v3_phoenix_m5_topology_intake_test tests.v3_rayjoin_pip_missing_author_test tests.v3_phoenix_m5_topology_packet_test
```

Result: 12 tests OK.

Passed:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
```

Result: 17 modules / 60 tests OK.

Passed:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
```

Result: pass, no violations.

## Goal-Level Decision Audit

Decision: close the bounded M5 author-code recovery goal as
`internal-author-complete`, not release evidence.

1. Was I foolish?

   Earlier in this goal, yes. The first recovery rerun reused an existing query
   CDB without writing parity-filter provenance, and the generated wording
   risked drifting toward a paper-reproduction implication.

2. What actions made it foolish?

   I treated a technically successful `query_exec` run as almost enough before
   ensuring the generated summary carried the same parity-filter and timing
   methodology evidence as the accepted artifact.

3. Was there another path?

   Yes. The better path was to rerun the author comparison through the same
   backend-parity-filtered generation path, then ask external review before
   closure.

4. Can I now try a different path that actually solves the problem?

   Yes. That path has been executed: rebuild author `query_exec`, rerun M5 with
   parity-filter provenance, document timing asymmetry, tag the generic
   capability, pass local gates, and close only the bounded internal evidence
   goal.

## Consensus

Codex accepts Claude's review and records that the bounded Phoenix V3 M5
author-code recovery goal is closed as internal evidence.

This does not authorize V3 release, public speedup wording, RayJoin paper
reproduction wording, full polygon overlay wording, or an `RTDL beats RayJoin`
claim. The next release-level step remains an M7 row-classification packet or
continued P0 work.
