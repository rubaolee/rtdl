# V4 Goal4781 Public Surface User Experience Polish

Date: 2026-06-27

Status: `local_ready_before_final_public_button`

## Release-Owner Requirement

Before the final public button, user-visible pages, links, docs, tutorials, and
examples must be:

- current-only;
- internally consistent;
- free of stale or misleading historical material;
- easy to follow without sending users into maintainer evidence;
- calm in tone, not framed as a wall of restrictions.

## Changes Made

This pass reduces user-facing friction without changing the V4.0.0 technical
claim boundary:

- README: removed first-page `history/` and `future/` layout rows and changed
  callback wording from "future work" to explicit planner-boundary wording.
- Current status and release notes: changed "not authorized" style wording into
  calmer claim-boundary wording.
- Public documentation map: keeps first-time user path focused on current docs
  and examples.
- App-level benchmark summary: keeps the complete matrix but avoids making the
  evidence path part of the first-time learning path.
- Tutorials: changed "unsupported/deferred/future work" tone to bounded planner
  result wording.
- Operator catalog and partner-choice guide: describe roadmap topics as outside
  the V4.0 public API, without making the tutorial feel like a failure list.
- Source-tree doctor: points users to current V4 checks instead of mentioning
  older compatibility scripts.

## Local Validation

```text
py -3 scripts/v4_universe_audit.py --format json --strict-release
status: pass
public_findings: []
unknown_untracked_count: 0

py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_release_clean_checkout_gate_test
Ran 16 tests in 34.882s
OK
```

## Tag Policy

This is a local pre-button polish change. If accepted, the final public button
must include:

1. commit this polish;
2. push the branch;
3. refresh `v4.0.0` to the new commit;
4. rerun local and Linux `--require-tag-head` gates;
5. rerun full V4 tests if no further edits are requested.

## Claim Boundary

This polish does not add new performance claims and does not authorize broad
all-app speedup, public true-zero-copy, raw OptiX callbacks, Tier-3 PTX/module
callbacks, C ABI/embedding, non-Python host bindings, or broad CuPy performance
claims.

