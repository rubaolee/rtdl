# Call For Review - Goal5442 X-HD Public Provenance Rescan

Please strictly review Goal5442.

## Files Under Review

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_goal5442_public_provenance_rescan.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5442_public_provenance_rescan.json
tests/goal5442_public_provenance_rescan_test.py
history/internal_docs/goal5442_xhd_public_provenance_rescan_2026-07-10.md
```

## Context

Goal5441 concluded that the full X-HD objective remains incomplete.  The primary
blocker is still:

```text
exact input artifacts or accepted exact-equivalence evidence
```

Goal5442 is a public provenance rescan after that gap matrix.  It is deliberately
not a POD run, not an author-code run, not an RTDL route run, and not a
performance goal.

Current result:

```text
status = public_provenance_rescan_no_new_exact_input_path__external_chain_still_needed
new_public_exact_input_artifact_found = false
exact_input_blocker_removed = false
pod_expected_next = false
```

Key observations:

```text
ACM proceedings page lists ics26-106.zip, but Goal5432 live checks still got 403 and no zip magic.
GitHub pwrliang/X-HD exists, but Goal5432 found no release asset, root data directory, or likely input dataset blob.
ArcGIS USA Detailed Water Bodies exists as a public source candidate, not author exact WKT bytes or hashes.
Crossref exposes no dataset/artifact link beyond the ACM article link.
```

## Stop-Loss Gate

```text
gate_generic_capability_produced: true
gate_non_app_consumer: public provenance rescan / exact-input blocker governance workflow
gate_requires_app_specific_logic: false
gate_downstream_consumer_reachable: true
```

This is governance/provenance work, not app-artifact parity implementation.

## Review Questions

1. Does Goal5442 correctly reuse and carry forward the Goal5432 live public
   artifact refresh instead of creating conflicting provenance evidence?
2. Is the distinction correct: ACM listing visibility does **not** equal ACM
   supplement inspection or exact input acquisition?
3. Is the distinction correct: ArcGIS public source candidates can support
   Level-B reconstruction but do **not** establish author exact WKT bytes or
   hashes?
4. Is it correct that GitHub source/scripts/logs and Crossref metadata still do
   not expose an exact input dataset archive?
5. Does the result correctly preserve the exact-input blocker:
   `exact_input_blocker_removed = false`?
6. Does the result correctly say POD is not expected next, because POD cannot
   manufacture missing public provenance?
7. Does the script avoid running POD, author code, RTDL routes, performance
   measurements, route tuning, or explicit `-lb` work?
8. Does the stop-loss gate pass as governance/provenance work rather than
   app-artifact parity work?
9. Is the next action correct: continue the external evidence chain, record a
   real response if one arrives, or inspect ACM supplement contents in an
   authorized environment before any runtime gate?

## Requested Verdict Labels

Approve:

```text
approve_goal5442_public_provenance_rescan_no_new_exact_input_path
```

Revise:

```text
revise_goal5442_public_rescan_before_using_as_blocker_status
```

Block:

```text
block_goal5442_if_public_listing_or_arcgis_candidate_is_overclaimed_as_exact_input
```

## Expected Answer Shape

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
```
