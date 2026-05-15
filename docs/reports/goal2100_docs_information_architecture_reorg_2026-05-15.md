# Goal2100 Docs Information Architecture Reorganization

Status: complete.

Purpose: make `docs/` clean for three reader groups:

- learners who want to write RTDL programs quickly;
- internal researchers who need deeper architecture and source-context notes;
- release reviewers who need logs, release evidence, reviews, and process
  material.

## New Structure

| Lane | Directory | Role |
| --- | --- | --- |
| Learner | `docs/learn/` | Curated current v2.0 learning path. |
| Research | `docs/research/` | Architecture, RayJoin/Embree research context, and future design notes. |
| Audit | `docs/audit/` | Process docs, runbooks, and links to evidence stores. |
| History | `docs/history/root_archive/` | Archived root-level goal logs and version notes removed from the front-door view. |

## Operations

| Area | Operation |
| --- | --- |
| `docs/README.md` | Rewritten around the three-door model: Learn, Research, Audit. |
| `docs/public_documentation_map.md` | Rewritten as an audience map instead of a flat topic map. |
| `docs/learn/README.md` | Added the fast learner path and current v2.0 design rule. |
| `docs/research/README.md` | Added advanced developer/research entry point. |
| `docs/research/rayjoin/` | Moved RayJoin, Embree, dataset, and paper reproduction notes out of root. |
| `docs/research/future/` | Moved future-looking and research-foundation notes out of root. |
| `docs/audit/process/` | Moved process and AI workflow docs out of root. |
| `docs/audit/runbooks/` | Moved RTX cloud runbook out of root. |
| `docs/history/root_archive/goal_logs/` | Moved archived root-level `goal_*.md` files out of root. |
| `docs/history/root_archive/version_notes/` | Moved archived root-level version notes out of root. |
| `docs/history/README.md` | Linked the new root archive and archived API/internal notes. |
| `docs/performance_model.md` | Replaced archive root version-doc links with current v2.0 support links. |

## Resulting Front-Door Shape

The top level of `docs/` now contains only current public pages and the clear
audience directories. Old logs and version notes no longer sit beside the
learner-facing docs in GitHub's directory browser.

## Regression Gate

`tests/goal2100_docs_information_architecture_reorg_test.py` checks:

- the three audience doors exist;
- root-level `docs/goal_*.md`, `docs/v0_*.md`, and `docs/v1_*.md` files are
  gone;
- root-level docs stay below a small, reviewable count;
- moved archive/research/process files exist at their new homes;
- `docs/README.md` and `docs/public_documentation_map.md` explain the new
  organization.

## Boundary

This is a documentation organization change. It does not change RTDL runtime
behavior or authorize v2.0 release.
