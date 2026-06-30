# Call For Review: User-Visible Surface Audit After v2.14 Cleanup

Date: 2026-06-30

Reviewer requested: Claude

Requested verdict labels:

- `approve_user_visible_surface_audit`
- `approve_with_required_fixes`
- `block_public_surface_until_fixed`

## Context

The repository public root has been restored to the RTDL v2.14 line. Post-v2.14
V3/V4 work is isolated outside the normal user path under `exp-project-1/`, and
old internal/history/review/handoff/report material has been moved under
`history/`.

The goal of this review is not to judge V3/V4. The goal is to verify that the
current public user path is clean, coherent, and safe for a new user who starts
from `README.md`.

Recent pushed commits on `main`:

- `3368c38dbf6f6836cdc880016930b16c4eb6ab02` — `Clean v2.14 public surface`
- `bbd1ffb0f47dd142bae4c68d20fbe49cabab9631` — `Add user-visible file audit`

Current `origin/main` was verified at:

```text
bbd1ffb0f47dd142bae4c68d20fbe49cabab9631
```

## Files To Review

Primary audit file:

- `history/internal_docs/user_visible_file_audit_2026-06-30.md`

Supporting cleanup records:

- `history/internal_docs/public_surface_separation_audit_2026-06-30.md`
- `history/internal_docs/public_surface_file_audit_2026-06-30.md`

Primary public entrypoints to inspect directly:

- `README.md`
- `docs/README.md`
- `tutorials/README.md`
- `tutorials/current/README.md`
- `examples/README.md`
- `examples/current/README.md`
- `docs/release_reports/v2_14/README.md`
- `docs/release_reports/v2_14/public_rt_vs_embree_comparison.md`
- `docs/release_reports/v2_14/public_wording_boundaries.md`

Public directories in scope:

- `docs/`
- `tutorials/`
- `examples/`

Excluded from user-facing audit scope:

- `src/`
- `tests/`
- `scripts/`
- `history/`
- `exp-project-1/`
- `.github/`
- local ignored artifacts

## Work Claimed By Main AI

1. User-facing docs now present one coherent current surface: RTDL v2.14.
2. Internal review, handoff, audit, report, and research records are archived
   under `history/`.
3. Post-v2.14 V3/V4 work is isolated under `exp-project-1/` and not part of the
   normal user path.
4. `docs/release_reports/v2_14/` is now a small public release package, not an
   internal closeout packet.
5. Public Markdown and public example Python files were scanned for internal
   process leaks.
6. A per-file audit was generated for 182 user-visible files.

## Claimed Validation Results

Public internal-leak scan over Markdown/Python/JSON/TXT:

```text
rg -n "\bGoal\d+|Claude|Gemini|Antigravity|Codex|CALL_FOR_REVIEW|review debt|verdict|v3\.0|v4\.0|RTDL V4|V4\.0|V3\.0" README.md docs tutorials examples --glob "*.md" --glob "*.py" --glob "*.json" --glob "*.txt" --glob "!history/**"
```

Claimed result: no matches.

Stale internal-path scan:

```text
rg -n "docs/(reports|reviews|handoff|audit|research|history)|examples/(internal|generated|legacy_or_backend_proofs|benchmark_apps)" README.md docs tutorials examples --glob "*.md" --glob "*.py" --glob "*.json" --glob "*.txt" --glob "!history/**"
```

Claimed result: no matches.

Markdown relative-link checker over `README.md`, `docs/**/*.md`,
`tutorials/**/*.md`, and `examples/**/*.md`, excluding `history/**`:

```text
ISSUES 0 FILES 88
```

Smoke / syntax checks:

```text
PYTHONPATH=src:. py -3 scripts\rtdl_source_tree_doctor.py
py -3 -m compileall -q examples\current
PYTHONPATH=src:. py -3 examples\current\getting_started\rtdl_hello_world.py
```

Claimed result: all passed. Source-tree doctor reported only optional
native/partner warnings.

## Questions For Claude

Please answer each question explicitly.

1. Does the audit scope match the user requirement: everything a normal user can
   reach from `README.md`, excluding source/runtime internals and development
   files?
2. Does the per-file audit genuinely give one row per user-visible file, with
   the four required answers:
   - should this file be here?
   - is the content correct?
   - does it contain history/error/internal leakage?
   - what remediation is recommended?
3. Do you find any remaining public-surface leakage of:
   - V3/V4 wording as current product truth,
   - internal goal numbers,
   - AI reviewer/process language,
   - old `docs/reports`, `docs/reviews`, `docs/handoff`, `docs/audit`,
     `docs/research`, or `docs/history` paths,
   - old generated/internal/legacy example paths?
4. Is `docs/release_reports/v2_14/` clean enough as a public release package, or
   does it still read like an internal closeout packet?
5. Are `history/` and `exp-project-1/` sufficiently separated from the normal
   learner path, while still preserved for maintainers?
6. Is the current README navigation likely to be comfortable for a new user, or
   does it still expose too much project churn?
7. Are there files in `docs/`, `tutorials/`, or `examples/` that should be moved
   out of the user-facing surface before public use?
8. Are there any broken links, stale references, or misleading performance
   claims that the main AI missed?
9. Does the evidence support approving this cleanup as the current public
   v2.14 surface?

## Required Review Style

Be strict. Do not reward the cleanup simply because it is large. If one
user-visible file still leaks internal process or creates a misleading current
product story, say so.

Classify findings as:

- P0: blocks public surface immediately;
- P1: must fix before calling the cleanup complete;
- P2: should fix, but does not block the current public surface;
- Note: non-blocking observation.

## Non-Authorization

This review must not authorize:

- V3 or V4 release claims;
- new benchmark performance claims;
- paper reproduction claims;
- changes to RTDL runtime/source behavior;
- package-install promises beyond the current source-tree v2.14 surface.

The only thing under review is whether the public-facing v2.14 documentation and
example surface is clean, coherent, and separated from internal/experimental
materials.
