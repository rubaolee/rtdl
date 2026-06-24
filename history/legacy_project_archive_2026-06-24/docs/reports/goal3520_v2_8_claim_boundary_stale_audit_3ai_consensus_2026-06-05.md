# Goal3520 3-AI Consensus: v2.8 Claim-Boundary And Stale-Doc Audit

Date: 2026-06-05

Status: internal closeout consensus; not release authorization.

## Scope

Goal3520 audited the v2.8 active learner/documentation surface and visible benchmark CLI/docstrings for stale current-version wording and accidental overclaiming. It also quarantined remaining versioned Python helper/protocol names as future alias/migration debt rather than renaming compatibility identifiers inside the closeout lane.

## Evidence Reviewed

- `docs/reports/goal3520_v2_8_claim_boundary_and_stale_doc_audit_2026-06-05.md`
- `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py`
- `docs/research/future_version_to_do_list.md`
- Root/docs learner Markdown surface
- Modified benchmark example files under `examples/v2_0/research_benchmarks/hausdorff_xhd`, `spatial_rayjoin`, and `rt_dbscan`
- External reviews:
  - `docs/reviews/goal3520_claude_review_v2_8_claim_boundary_stale_audit_2026-06-05.md`
  - `docs/reviews/goal3520_gemini_review_v2_8_claim_boundary_stale_audit_2026-06-05.md`

## Validation

Local validation after review-response edits:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3520_v2_8_claim_boundary_stale_audit_test \
  tests.goal3519_v2_8_learner_docs_cleanup_test \
  tests.goal3518_v2_8_benchmark_matrix_test

Ran 14 tests in 0.190s
OK
```

Additional checks:

```text
rg -n "v2\.x|release package|full rayjoin reproduction is authorized|rtdl beats rayjoin is authorized|true zero-copy authorized|public speedup claim authorized" README.md docs/README.md docs/learn docs/tutorials examples/v2_0/research_benchmarks docs/research/future_version_to_do_list.md
```

The scan returned no matches.

The modified benchmark Python files also passed `py_compile`.

## Review Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | `accept-with-boundary` | Goal is an internal closeout audit only; legacy versioned helper names remain quarantined compatibility/protocol debt. |
| Claude | `accept-with-boundary` | Confirmed active learner Markdown is v2.8-current, Python display strings are cleaned, and no release/public-claim authorization is introduced. Noted low-risk test gaps around recursive Markdown coverage and Python claim-boundary literals. |
| Gemini | `accept-with-boundary` | Accepted the quarantine and boundary discipline. Flagged root README `Historical Release Package` wording and asked for stronger claim-boundary test coverage. |

## Review-Response Changes

After the external reviews, Goal3520 added two small hardenings:

- Root README historical links were rephrased from `Historical v2.6/v2.3 Release Package` to `Historical v2.6/v2.3 Evidence Archive`, preserving history while removing package/release wording from the front door.
- `tests/goal3520_v2_8_claim_boundary_stale_audit_test.py` now recursively scans active Markdown and blocks literal `True` assignments for critical release, speedup, zero-copy, paper-reproduction, RayJoin, hidden-dispatcher, and RT-core claim-boundary keys in benchmark Python.

## Consensus

Consensus verdict: `accept-with-boundary`.

Goal3520 is accepted as a v2.8 internal closeout audit gate. It improves the active learner surface and example display strings, adds fail-closed stale-doc and claim-boundary checks, preserves negative boundary language, and records legacy versioned helper names as future migration debt.

This consensus does not authorize a v2.8 public release, package-install claim, public speedup claim, broad RT-core claim, true zero-copy claim, full paper/RayJoin reproduction claim, hidden partner-selection behavior, or app-specific native-engine behavior.

## Remaining Boundary

The remaining debt is intentionally deferred: selected Python compatibility/protocol helper names still contain `v2_5` or `v2_6`. A future alias/migration goal should decide whether to rename or alias them, with compatibility tests and artifact-schema preservation. This boundary does not block the v2.8 internal closeout.
