# Goal648 Public Release Hygiene Check

Date: 2026-04-20

Verdict: ACCEPT with Codex, Claude, and Gemini Flash consensus.

## Scope

Goal648 checks the public release surface after the `v0.9.5` release and
post-release fresh-checkout verification. The focus is what a GitHub visitor
will see first:

- front-page `README.md`
- documentation index `docs/README.md`
- tutorials and examples indexes
- current release package
- visible history indexes and revision dashboard
- older visible release packages that could be mistaken for current release
  state

## Findings

The existing front-page and command checks were already green:

- `v0.9.5` is the current released version in the public front-page docs.
- Public runnable command audit covers `248` commands across `14` public docs.
- Public command audit result remains `valid: true`.
- Focused public docs tests still pass.

One real hygiene issue was found:

- `history/README.md` and `history/COMPLETE_HISTORY.md` still described the
  archive as current only through `v0.9.4` or older top rounds.
- The released `v0.9.5` tag and Goal645-647 release/fresh-checkout chain were
  not visible enough from the history entry points.

One confusing historical package was also clarified:

- `docs/release_reports/v0_9_2/` was a visible internal Apple RT candidate
  package. It already said candidate in several places, but a new visitor could
  still mistake the folder name and title for a public release package.

## Changes Made

- Updated `history/README.md` to state that the archive now includes `v0.9.5`
  release, post-release front-page refresh, and fresh-checkout verification
  records.
- Updated `history/COMPLETE_HISTORY.md` to include the `v0.9.5` release tag and
  current top rounds for Goal645, Goals641-644, Goal646, and Goal647.
- Added explicit public-status notes to:
  - `docs/release_reports/v0_9_2/README.md`
  - `docs/release_reports/v0_9_2/release_statement.md`
  - `docs/release_reports/v0_9_2/tag_preparation.md`
- Updated `docs/release_reports/v0_9/support_matrix.md` to clarify that it is a
  historical `v0.9.0`/`v0.9.1` matrix and that `v0.9.2` was later absorbed into
  released `v0.9.4`.
- Added `tests/goal648_public_release_hygiene_test.py` so stale public-history
  and `v0.9.2` public-release ambiguity are caught by tests.
- Registered `2026-04-20-goal648-public-release-hygiene-check` in
  `history/history.db`, regenerating `history/revision_dashboard.md` and
  `history/revision_dashboard.html`. The dashboard now has a current `v0.9.5`
  top row for Goal648.

## Verification

Focused public release hygiene suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal648_public_release_hygiene_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal532_v0_8_release_authorization_test \
  tests.goal512_public_doc_smoke_audit_test -v
```

Result:

```text
Ran 17 tests in 0.031s
OK
```

Public command truth audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```json
{
  "command_count": 248,
  "public_doc_count": 14,
  "valid": true
}
```

Public entry smoke check:

```text
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
```

Result: `valid: true`, with no link failures and no phrase failures.

Whitespace check:

```text
git diff --check
```

Result: no output, no failure.

## Remaining Boundaries

- Historical reports are not rewritten to look current.
- Older release packages remain visible as historical packages.
- `history/revisions/` remains a structured round archive, not one directory
  per goal.
- The history dashboard is generated from `history/history.db`; Goal648
  registers a new round so the dashboard has a current top entry.

## External AI Reviews

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal648_claude_review_2026-04-20.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal648_gemini_flash_review_2026-04-20.md`

Both external reviews returned `ACCEPT`. Claude verified the changed history
indexes, `v0.9.2` clarification, historical `v0.9` support matrix note, test
evidence, and honesty boundary. Gemini Flash accepted the GitHub-facing
`v0.9.5` hygiene fixes as correct and appropriately bounded.

## Codex Verdict

ACCEPT. The user-facing public release surface is now consistent with the
actual `v0.9.5` release state, and the specific stale-history failure mode is
covered by a regression test.
