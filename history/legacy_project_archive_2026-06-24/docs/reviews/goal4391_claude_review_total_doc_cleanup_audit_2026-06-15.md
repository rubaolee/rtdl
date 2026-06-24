# Goal4391 Claude Review: Total Documentation Cleanup Audit

Date: 2026-06-15

Reviewer: Claude (claude-sonnet-4-6)

VERDICT: ACCEPT_WITH_NOTES

---

## Scope

Reviewed all artifacts referenced in the Goal4391 handoff:

- `scripts/rtdl_total_doc_cleanup_audit.py`
- `tests/goal4391_total_doc_cleanup_audit_test.py`
- `README.md` (first 60 lines)
- `docs/versioning.md`
- `docs/release_reports/v2_13/README.md`
- `docs/release_reports/v2_13/publication.md`
- `docs/release_reports/v2_13/release_publication.json`
- `docs/reports/goal4386_v2_14_final_closeout_2026-06-15.md`
- `docs/audit/process/current_milestone_qa.md`
- `docs/engineering/handoffs/V0_4_FINAL_RELEASE_HANDOFF_HUB.md`

The MD/JSON audit outputs (`goal4391_total_doc_cleanup_audit_2026-06-15.md` and `.json`) exceed the read limit at 2 MB and 5.8 MB respectively; findings below are based on the script logic, test suite, and per-file spot-checks, which is sufficient to evaluate all 10 claims.

---

## Claim-by-Claim Assessment

**Claim 1 — Current-facing docs no longer claim v2.13 is current.**
Pass. `README.md` line 16 reads "current v2.14 source-tree RTDL surface". `docs/versioning.md` status line reads "current v2.14 source-tree guidance" and the Current Version section names `v2.14` throughout. Test `test_current_version_entry_points_are_v2_14` checks five canonical entry points for presence of "v2.14" and absence of "current v2.13" / "v2.13 is the current".

**Claim 2 — Current-facing docs have zero stale current-version hits.**
Pass. Audit summary `stale_current_version_hits: 0`. The `STALE_CURRENT_RE` covers eight documented phrase forms specific to the v2.13→v2.14 transition. Test gate enforces this stays zero on every run.

**Claim 3 — Current-facing docs have zero draft/pending release wording hits.**
Pass. Audit summary `draft_or_pending_hits: 0`. The `DRAFT_RELEASE_RE` covers seven key draft/pending phrases. The `CURRENT_DOC_ALLOW_DRAFT_PHRASE` escape hatch is narrowly scoped to `docs/release_reports/v0_4_preview/` only.

**Claim 4 — Current-facing docs have zero dead internal links.**
Pass. Audit summary `current_dead_internal_links: 0`. The link resolver correctly handles relative paths, fragment-only links, external links, and fenced-code blocks (skipped during extraction). Test gate enforces zero.

**Claim 5 — v2.13 release docs are marked as a previous release superseded by v2.14.**
Pass. `docs/release_reports/v2_13/README.md` contains "v2.13 is now a previous source-tree release. The current source-tree release is [v2.14]". `docs/release_reports/v2_13/publication.md` contains "preserved as previous-release evidence rather than the current source-tree release note" and "the current release is v2.14". `release_publication.json` carries `"superseded_by": "v2.14"` and a corrected `release_statement`. Test `test_v2_13_docs_are_marked_superseded` verifies the MD files with exact string assertions.

**Claim 6 — v2.14 docs remain release-current and do not revert to draft/pending wording.**
Pass. `docs/reports/goal4386_v2_14_final_closeout_2026-06-15.md` records "maintainer authorization was later given, the version marker moved to v2.14, and tag `v2.14` was created and pushed." Zero draft/pending hits from the audit. Test entry-point checks find `v2.14` in all five canonical paths.

**Claim 7 — Historical/evidence files are not rewritten to erase history.**
Pass. The audit script explicitly classifies files before acting. Historical files with dead links or old version mentions receive action `"preserved_as_historical_or_evidence; old links/status belong to frozen audit context unless revived"` rather than silent correction. The 2,557 historical dead internal links are documented, not hidden. `HISTORICAL_PREFIXES` is a comprehensive list covering `docs/history/`, `docs/reports/`, `docs/reviews/`, `docs/handoff/`, `docs/patches/`, `docs/engineering/handoffs/`, `docs/research/archive/`, and all release-report paths through `v2_13`. Historical content examined (`V0_4_FINAL_RELEASE_HANDOFF_HUB.md`) is correctly self-described as an archived checklist and classified as historical by path.

**Claim 8 — Per-document report satisfies the requested shape.**
Pass. The markdown renderer produces a table with columns: Document, Class, Links, Issues, Finding, Action. Each scanned file gets one row. Finding collapses up to three issue codes with line numbers, plus a `+N more` overflow. Action is either a CLEANUP_ACTIONS entry or a policy string. Test `test_report_records_per_document_actions` verifies the report contains the summary gate lines, a `README.md` row, the specific fix phrase for README, and the historical-evidence policy paragraph.

**Claim 9 — Regression test locks the important gates.**
Pass. `test_current_facing_docs_have_no_actionable_issues` asserts all four summary counters are zero on a live `build_payload()` run, so the lock applies to the actual repository state, not a snapshot. The test suite runs as part of the 63-test suite (all OK). The test is deterministic against the filesystem, which is the right anchor for this type of gate.

**Claim 10 — v2.14 tag remains on the release commit, not the post-release docs commit.**
Pass. `git tag -l` confirms `v2.14` points to `8384a38376567fe518d89721453eb4433de08312` ("Release RTDL v2.14 benchmark cleanup packet"), not to `ee0fdab45b785b7c99675f3bb6242aec1dead6fd` ("Audit and refresh documentation for v2.14"). The handoff explicitly states the tag was intentionally not moved, and this is verified.

---

## Notes

**N1 — JSON files are outside the audit scan.**
`DOC_GLOBS` is `("*.md", "*.rst", "*.txt")`. The `release_publication.json` update (adding `superseded_by` and correcting `release_statement`) was made manually and is not automatically checked by the audit tool or regression test. The JSON content is correct as read, but no gate will catch a future accidental revert of that file. This is a known scope boundary, not a defect introduced by Goal4391, and is acceptable given the corresponding MD files do carry the supersession wording that the test checks.

**N2 — `docs/audit/process/current_milestone_qa.md` is classified as current-facing despite self-describing as historical context.**
The file opens with "This page is preserved historical context for maintainers." Its path (`docs/audit/process/`) matches the `docs/` current prefix and no historical prefix, so the audit tool classifies it as `current_facing`. The links were repaired as part of Goal4391 (CLEANUP_ACTIONS entry) and now pass the dead-link gate. The content discusses v0.7, v0.6, and earlier milestones and does not trigger STALE_CURRENT_RE or DRAFT_RELEASE_RE because those patterns are scoped to v2.13/v2.14 transition phrases only. This pre-existing organizational mismatch is not introduced by Goal4391, and the file does warn readers it is not the primary user-learning path entry. No fix required for Goal4391 closeout.

**N3 — STALE_CURRENT_RE covers documented phrase forms but not all paraphrases.**
The eight pattern alternatives cover the phrases actually used in this repository's documentation style (e.g., "current v2.13", "RTDL v2.13 is the current"). Less common paraphrases such as "currently v2.13" or "latest v2.13" are not matched. Given zero hits in a 113-file current scan and the explicit test gate, this is sufficient for closeout. If the v2.15 cleanup repeats this process, the pattern set should be extended before scanning.

**N4 — 2,557 historical dead internal links are a future maintenance burden.**
The preservation policy is sound for an audit-style project where historical reports must remain frozen. Reviewers picking up a future release cycle should be aware that any link fixes to historical files would require a policy exception. The current approach of reporting-rather-than-rewriting is correct for this cycle.

---

## Summary

All ten claims from the handoff check out. The current-reader documentation path is clean: zero stale v2.13-current hits, zero draft/pending wording hits, zero dead internal links, v2.13 release docs correctly superseded, v2.14 tag on the right commit. The audit tool and test suite are structurally sound and will prevent regression. Historical files are preserved, not rewritten. The per-document report shape matches what was requested.

The notes above identify scope boundaries and pre-existing organizational issues; none require a fix before Goal4391 closeout.

VERDICT: ACCEPT_WITH_NOTES
