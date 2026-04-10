# History Capture And External Artifact Import

Date: 2026-04-10
Repo:
- `/Users/rl2025/rtdl_python_only`

## Purpose

Record the recent external/parallel-checkout artifacts that were not yet stored
inside the main repository, then import the ones worth preserving so the
project's historical trail stays inside the repo instead of being split across
ad hoc local directories.

This report is intentionally procedural. It says what was reviewed, what was
imported, what was left external-only, and why.

## Source Locations Reviewed

Parallel Gemini checkout:
- `/Users/rl2025/antigravity-working/rtdl`

External Claude work directory:
- `/Users/rl2025/claude-work`

Reviewed source files:
- `/Users/rl2025/antigravity-working/rtdl/docs/reports/RTDL_v0.3_Final_Audit_Report_2026-04-09.md`
- `/Users/rl2025/antigravity-working/rtdl/docs/reports/RTDL_Wiki_Generation_Report_2026-04-09.md`
- `/Users/rl2025/antigravity-working/rtdl/docs/wiki_drafts/Home.md`
- `/Users/rl2025/antigravity-working/rtdl/docs/wiki_drafts/Quick-Start.md`
- `/Users/rl2025/antigravity-working/rtdl/docs/wiki_drafts/Core-Concepts.md`
- `/Users/rl2025/antigravity-working/rtdl/docs/wiki_drafts/Backends.md`
- `/Users/rl2025/antigravity-working/rtdl/docs/wiki_drafts/Example-Gallery.md`
- `/Users/rl2025/claude-work/rtdl_v0_4_code_audit_2026-04-10.md`

## Review And Import Decisions

### 1. `RTDL_v0.3_Final_Audit_Report_2026-04-09.md`

Decision:
- already imported earlier as an external audit artifact
- raw source body also preserved in this round

Current repo file:
- [RTDL_v0_3_Final_Audit_Report_2026-04-09_external.md](/Users/rl2025/rtdl_python_only/docs/reports/RTDL_v0_3_Final_Audit_Report_2026-04-09_external.md)
- [external_raw/RTDL_v0.3_Final_Audit_Report_2026-04-09.md](/Users/rl2025/rtdl_python_only/docs/reports/external_raw/RTDL_v0.3_Final_Audit_Report_2026-04-09.md)

Action in this round:
- reviewed and retained as-is
- no second duplicate copy created

### 2. `RTDL_Wiki_Generation_Report_2026-04-09.md`

Decision:
- imported into the main repo as an external documentation artifact

Current repo file:
- [RTDL_Wiki_Generation_Report_2026-04-09_external.md](/Users/rl2025/rtdl_python_only/docs/reports/RTDL_Wiki_Generation_Report_2026-04-09_external.md)
- [external_raw/RTDL_Wiki_Generation_Report_2026-04-09.md](/Users/rl2025/rtdl_python_only/docs/reports/external_raw/RTDL_Wiki_Generation_Report_2026-04-09.md)

Reason:
- it explains where the parallel wiki drafts came from and why they exist

### 3. Parallel `docs/wiki_drafts/*.md`

Decision:
- imported into the main repo under
  [docs/wiki_drafts](/Users/rl2025/rtdl_python_only/docs/wiki_drafts)
- preserved as historical drafts, not promoted to live docs

Imported files:
- [README.md](/Users/rl2025/rtdl_python_only/docs/wiki_drafts/README.md)
- [Home.md](/Users/rl2025/rtdl_python_only/docs/wiki_drafts/Home.md)
- [Quick-Start.md](/Users/rl2025/rtdl_python_only/docs/wiki_drafts/Quick-Start.md)
- [Core-Concepts.md](/Users/rl2025/rtdl_python_only/docs/wiki_drafts/Core-Concepts.md)
- [Backends.md](/Users/rl2025/rtdl_python_only/docs/wiki_drafts/Backends.md)
- [Example-Gallery.md](/Users/rl2025/rtdl_python_only/docs/wiki_drafts/Example-Gallery.md)

Reason:
- the content is useful history
- the pages are not guaranteed to match current live docs
- storing them with a disclaimer preserves the work without misleading readers

### 4. `rtdl_v0_4_code_audit_2026-04-10.md`

Decision:
- imported into the main repo as an external audit artifact

Current repo file:
- [rtdl_v0_4_code_audit_2026-04-10_external.md](/Users/rl2025/rtdl_python_only/docs/reports/rtdl_v0_4_code_audit_2026-04-10_external.md)
- [external_raw/rtdl_v0_4_code_audit_2026-04-10.md](/Users/rl2025/rtdl_python_only/docs/reports/external_raw/rtdl_v0_4_code_audit_2026-04-10.md)

Reason:
- the audit produced the real `query_id` ordering finding that directly led to
  the current-repo correctness fix at commit `9624dcd`
- the audit itself belongs in the history trail alongside the fix

### 5. Parallel macOS portability stash

Source inspected:
- `git -C /Users/rl2025/antigravity-working/rtdl stash show -p stash@{0}`

Decision:
- not imported in this round

Reason:
- it contains implementation proposals from a parallel checkout, not just
  stable historical artifacts
- some parts may still be useful, but they require a separate bounded review
  before changing current `main`
- importing the reports now preserves history without over-claiming that the
  stash logic has already been adopted

## Docs Surface Update

The docs index was updated in this round to make the imported historical
artifacts discoverable from inside the main repo, instead of leaving them only
in external directories.

## Result

After this round, the main repo now contains:

- the external Gemini `v0.3` final audit artifact
- the external Gemini wiki-generation artifact
- the external Claude `v0.4` audit artifact
- verbatim raw copies of those external reports
- the imported wiki draft pages from the parallel checkout
- this ledger explaining what was imported and what was intentionally left out

That gives the repo a stronger self-contained history trail for both the `v0.3`
closure and the early `v0.4` line.
