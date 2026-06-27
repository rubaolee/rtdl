# V4 Public Docs Full Audit Action Summary

Date: 2026-06-27

Scope: root `README.md` plus every Markdown file currently under `docs/`.

Intent: make the public V4 documentation read like a current product surface,
not a mixture of user guidance, internal release defense, old version history,
and reviewer-facing wording.

## Actions By File

| File | Action |
| --- | --- |
| `README.md` | Rewritten as the clean project entrypoint. Removed internal status/closure wording and negative claim-boundary lists. Kept the current V4 import, V2/V3 superset explanation, quickstart, current user paths, and a short performance snapshot. |
| `docs/README.md` | Rewritten as a short documentation index. The first-time path now points to release notes, current status, operator catalog, partner choice, benchmarks, tutorials, and examples. Historical material is explicitly routed to `history/`. |
| `docs/current_v4_status.md` | Rewritten as a user-facing status page. Removed machine decision label, internal status block, and public-claim prohibition list. Kept current capabilities, measured surfaces, benchmark snapshot, V4.0 exclusions, and quick checks. |
| `docs/v4_release_notes.md` | Rewritten as concise release notes. Removed legalistic boundary phrasing and kept highlights, performance reading, and the learning path. |
| `docs/app_level_benchmark_summary.md` | Rewritten from mixed internal/external wording into a reader-facing benchmark report. Removed decision label, allowed/disallowed wording blocks, and maintainer evidence language. Kept the 10-app table, V4-specific workflow row, and plain-English row notes for Hausdorff, Barnes-Hut, and Spatial RayJoin. |
| `docs/public_documentation_map.md` | Rewritten to show only the current first-time user path, quick check commands, and archive location. Removed `performance_wording.md` from the main learning sequence. |
| `docs/v4_engineering_summary.md` | Rewritten as a compact maintainer note. Removed process-heavy phrasing and kept architecture, current release checks, matrix facts, and partner policy. |
| `docs/learn/README.md` | Rewritten as a compact reference index. It now explains which files are learning references instead of presenting every note as a first-time tutorial. |
| `docs/learn/operator_catalog.md` | Cleaned as the current operator catalog. Clarified that these are generic RT-shaped operators/workflows, added an upfront denominator reminder, and kept runnable example commands. |
| `docs/learn/partner_choice.md` | Reviewed and left structurally unchanged. It was already user-facing: explicit partner choices, bounded request behavior, and practical rules. |
| `docs/learn/performance_wording.md` | Rewritten from a claim-prohibition guide into "Reading Performance Results." It now teaches users how to read denominators, hardware paths, app rows, operator rows, and table distributions. |
| `docs/learn/source_tree_doctor.md` | Rewritten as "Check Your Checkout." It now gives short user/developer commands without release-procedure framing. |

## Test And Gate Updates

| File | Action |
| --- | --- |
| `tests/v4_frontdoor_test.py` | Updated README assertions to match the cleaner user-facing entrypoint. The test now verifies current V4 import, V2/V3 superset wording, benchmark-table reading, and absence of old boundary-list phrasing. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Updated operator/performance assertions so the gate checks positive user-facing wording rather than requiring old internal claim-boundary text. |
| `tests/v4_goal4743_public_docs_current_framing_test.py` | Updated to block internal decision labels from current public docs and verify the table facts remain visible. |
| `tests/v4_goal4646_pretag_wording_fixes_test.py` | Updated distribution checks so detailed operator distribution wording lives in the relevant reference docs rather than being forced into every top-level user page. |

## Verification

Commands run:

```powershell
py -3 scripts\v4_universe_audit.py
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test tests.v4_goal4743_public_docs_current_framing_test tests.v4_goal4646_pretag_wording_fixes_test
```

Results:

- `v4_universe_audit.py`: `status = pass`, `public_findings = []`, `unknown_untracked_count = 0`.
- Target public docs/frontdoor/wording tests: `29 tests OK`.

## Remaining Note

This pass covers root `README.md` and every Markdown file under `docs/`.
Benchmark app source files still contain historical variable names and internal
metadata in code paths. They are not part of this docs pass, but they are a
separate candidate for a later code-facing cleanup if the project wants the
GitHub source view of benchmark harnesses to be as clean as the docs surface.
