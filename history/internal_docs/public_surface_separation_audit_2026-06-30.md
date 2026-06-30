# Public Surface Separation Audit

Date: 2026-06-30

Purpose: record the cleanup that separates the user-facing RTDL v2.14 surface
from internal history, review records, handoffs, and experimental work.

## Current User-Facing Surface

Users should start from:

- `README.md`
- `tutorials/`
- `docs/`
- `examples/current/`
- `docs/release_reports/v2_14/`

The current public story is RTDL v2.14. The normal learner path should not
require any internal review records, handoff files, archived release records, or
experimental project material.

The root README distinguishes normal user entries (`tutorials/`, `docs/`,
`examples/`) from maintainer entries (`scripts/`, `tests/`) and the isolated
experimental project archive (`exp-project-1/`).

## Internal / Historical Surface

The following materials are archived away from the first-user path:

- old `docs/audit`, `docs/directives`, `docs/engineering`, `docs/handoff`,
  `docs/patches`, `docs/reports`, `docs/research`, `docs/reviews`,
  `docs/sql`, and `docs/history` trees;
- old release-report packages other than the current v2.14 public package;
- generated/internal/backend-proof examples;
- old research-benchmark walkthrough files that were process notes rather than
  current learner documentation.
- the untracked `tools/_archive` directory, moved to
  `history/internal_docs/tools_archive/`.

Historical material is preserved under:

- `history/internal_docs/`
- `history/release_reports/`
- `history/examples_internal/`

## Public Docs After Cleanup

The public docs now use these rules:

- no internal goal identifiers in the normal user-facing Markdown surface;
- no external-AI reviewer names in the normal user-facing Markdown surface;
- no V3/V4 wording in the normal user-facing Markdown surface;
- no internal goal identifiers or old-process links in public example Python
  files under `examples/current/`;
- no links to removed `docs/reports`, `docs/reviews`, `docs/handoff`,
  `docs/audit`, `docs/research`, or `docs/history` paths;
- no broken relative Markdown links in `README.md`, `docs/`, `tutorials/`, or
  `examples/`.

## Validation Performed

Commands run from the repository root:

```text
rg -n "\bGoal\d+|Claude|Gemini|Antigravity|Codex|CALL_FOR_REVIEW|review debt|verdict|docs/(reports|reviews|handoff|audit|research|history)|examples/(internal|generated|legacy_or_backend_proofs|benchmark_apps)|v2\.10|v4\.0\.0|RTDL V4|V4\.0" README.md docs tutorials examples --glob "*.md" --glob "!history/**"
```

Result: no matches.

```text
rg -n "\bv3\b|\bV3\b|\bv4\b|\bV4\b|V3\.0|V4\.0|v3\.0|v4\.0|RTDL V4" README.md docs tutorials examples --glob "*.md" --glob "!history/**"
```

Result: no matches.

```text
rg -n "\bGoal\d+|Claude|Gemini|Antigravity|Codex|CALL_FOR_REVIEW|review debt|verdict|v3\.0|v4\.0|RTDL V4|V4\.0|V3\.0" examples/current examples/README.md tutorials docs --glob "*.py" --glob "*.md" --glob "!history/**"
```

Result: no matches.

```text
rg -n "docs/(reports|reviews|handoff|audit|research|history)|examples/(internal|generated|legacy_or_backend_proofs|benchmark_apps)" README.md docs tutorials examples --glob "*.py" --glob "*.md" --glob "!history/**"
```

Result: no matches.

Relative Markdown link check over `README.md`, `docs/**/*.md`,
`tutorials/**/*.md`, and `examples/**/*.md`, excluding `history/**`:

```text
ISSUES 0 FILES 88
```

Source-tree smoke checks:

```text
RTDL Source Tree Doctor: core checks passed; optional native/partner warnings only.
examples/current/getting_started/rtdl_hello_world.py: passed.
examples/current/getting_started/rtdl_primitive_discovery_workflow.py: passed.
examples/current/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py --backend cpu_python_reference: passed.
python -m compileall -q examples/current: passed.
```

Root cleanup:

- empty local `artifacts/` directory removed;
- untracked top-level `tools/_archive` moved under
  `history/internal_docs/tools_archive/`;
- root README now labels `scripts/` and `tests/` as maintainer entries and
  `exp-project-1/` as an experimental archive outside the current user surface.

## Remaining Principle

If a file exists to explain old process, old releases, review debt, or
experimental branches, it belongs in `history/` or the explicit experimental
project directory, not in the first-user path.
