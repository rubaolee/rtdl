# Goal 646: Post-Release Public Front-Page Documentation Update

Date: 2026-04-19

## Scope

Post-v0.9.5 public documentation cleanup focused on front pages that real users
see first:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/backend_maturity.md`

Goal: make the public entry path correct, consistent, and professional after
the `v0.9.5` release.

## Changes

- Tightened the root README opening to explain RTDL as a Python-hosted
  ray-tracing-style search language/runtime.
- Kept the v0.9.5 front-page feature boundary explicit:
  `ray_triangle_any_hit`, `visibility_rows`, and `reduce_rows`.
- Kept the accelerator honesty boundary explicit:
  native early-exit any-hit exists for OptiX, Embree, and HIPRT; Vulkan and
  Apple RT are compatibility paths; `reduce_rows` is not a native backend
  reduction.
- Shortened the docs index new-user path from a release-history-heavy path to a
  focused current-product path.
- Left historical release packages linked in the docs index for auditability
  instead of presenting them as required first-read material.
- Fixed the maintainer refresh note that still described v0.9.4 as current.
- Added a regression test for stale release-control wording and v0.9.5
  front-page consistency.

## Verification

Stale wording audit:

```text
rg -n 'release-candidate|candidate package|release-prepared|tag not|user-controlled|current active development|v0\.9\.5.*candidate|v0\.9\.4 is now the current|current `v0\.9\.4|current v0\.9\.4|current released version remains|active `v0\.9\.5`|at the user' \
  README.md docs/README.md docs/current_architecture.md docs/capability_boundaries.md docs/rtdl_feature_guide.md docs/release_facing_examples.md docs/tutorials/README.md examples/README.md docs/quick_tutorial.md docs/backend_maturity.md docs/release_reports/v0_9_5 /Users/rl2025/refresh.md
```

Expected result:

```text
no stale public-doc matches
```

Regression test added:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal646_public_front_page_doc_consistency_test -v
```

Focused verification actually run:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal646_public_front_page_doc_consistency_test tests.goal645_v0_9_5_release_package_test tests.goal515_public_command_truth_audit_test tests.goal532_v0_8_release_authorization_test -v

Ran 11 tests in 0.016s
OK
```

Whitespace audit:

```text
git diff --check
```

Result:

```text
no output
```

## Verdict

Codex verdict: ACCEPT.

The public front pages are consistent with the released `v0.9.5` state, the
new-user path is concise, and stale release-control wording is absent from the
checked public entry pages.

## External Reviews

Claude review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal646_claude_review_2026-04-19.md`
- Verdict: ACCEPT.
- Finding: no correctness, consistency, or professionalism blockers.

Gemini Flash review:

- File: `/Users/rl2025/rtdl_python_only/docs/reports/goal646_gemini_flash_review_2026-04-19.md`
- Verdict: ACCEPT.
- Finding: no public-doc correctness, consistency, or professionalism blockers.

Final consensus:

- Codex: ACCEPT.
- Claude: ACCEPT.
- Gemini Flash: ACCEPT.
