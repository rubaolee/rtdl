# Claude Review Task: Goal3058 v2.6 Documentation Total Audit

Please perform an independent Claude review of the v2.6 release-candidate
documentation cleanup and total audit.

## Required Output

Write your review to:

`docs/reviews/goal3059_claude_review_goal3058_v2_6_doc_total_audit_2026-06-02.md`

Use one of these verdicts: `accept`, `accept-with-boundary`, `reject`, or
`needs-more-evidence`.

## Context

The user set a release-blocking rule:

- current learner/user/current-research docs must present a single v2.6 surface;
- older version information must live in historical/archive dirs, not normal
  learner paths;
- docs must avoid wrong, inconsistent, outdated, redundant examples, links, and
  terms;
- every current-facing file needs an audit log entry;
- tutorial/example runnable validation remains a separate gate when pod/native
  resources are needed;
- v2.6 release requires 3-AI consensus, so this review is one external input,
  not release authorization by itself.

## Files To Read

- `docs/reports/goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md`
- `tests/goal3058_v2_6_release_candidate_doc_total_audit_test.py`
- `tests/goal3056_v2_6_pre_release_public_doc_cleanup_audit_test.py`
- `README.md`
- `docs/README.md`
- `docs/current_architecture.md`
- `docs/partner_acceleration_boundaries.md`
- `docs/public_documentation_map.md`
- `docs/app_engine_support_matrix.md`
- `docs/app_example_quickstart.md`
- `docs/research/README.md`
- `docs/research/archive/README.md`
- `examples/README.md`
- `examples/v2_0/README.md`
- `examples/v2_0/research_benchmarks/raydb_style/README.md`

Also inspect the current git diff for renamed files under `docs/research/archive/`.

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3058_v2_6_release_candidate_doc_total_audit_test tests.goal3056_v2_6_pre_release_public_doc_cleanup_audit_test tests.goal3054_v2_6_partner_choice_guidance_test tests.goal3050_partner_choice_docs_test tests.goal3052_partner_choice_pod_refresh_test tests.goal2806_v2_5_internal_readiness_packet_test
```

## Review Questions

1. Do the current-facing docs now present a coherent v2.6 release-candidate
   surface without making users juggle v2.3/v2.5/pre-release history?
2. Were older research/proposal/transition files moved into a sufficiently
   explicit archive lane without breaking current navigation?
3. Does the audit report cover each current-facing file and each moved archive
   file with status, old problem, action, and explanation?
4. Are any live docs still wrong, stale, redundant, link-broken, overclaiming,
   or inconsistent with primitive-first/user-chosen-partner v2.6 guidance?
5. Are release boundaries still blocked correctly until tutorial/example
   runnable validation and final 3-AI consensus?

Please lead with findings by severity. If there are no blocking findings, say
so explicitly and name any residual release-gate work.
