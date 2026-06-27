# Goal682 Consensus: v0.9.6 Release-Candidate Package

Status: ACCEPT

Date: 2026-04-21

## Scope

Goal682 packages the accepted post-`v0.9.5` current-main
prepared/prepacked visibility-count optimization work as a `v0.9.6` release
candidate.

Primary report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal682_v0_9_6_release_candidate_package_2026-04-21.md`

External reviews:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal682_external_review_claude_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal682_external_review_gemini_flash_2026-04-21.md`

## Consensus

Codex, Claude, and Gemini Flash all accept Goal682.

Agreed findings:

- `v0.9.6` is clearly marked as a release candidate only.
- The current public release remains `v0.9.5`.
- Tag and push commands are documented only as held commands.
- Maintainer authorization is still required before tag/push.
- Public docs link the candidate package without changing current-release
  wording.
- No broad DB, graph, full-row, one-shot, GTX 1070 RT-core, AMD GPU, or Apple
  RT full-row speedup claim is made.

## Verification

Focused package/public-doc regression:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal682_v0_9_6_release_candidate_package_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal655_tutorial_example_current_main_consistency_test -v

Ran 17 tests in 0.005s
OK
```

Public command truth audit:

```text
valid: true
command_count: 250
public_doc_count: 14
```

Public entry smoke:

```text
valid: true
```

Whitespace check:

```text
git diff --check

clean
```

## Verdict

Goal682 is accepted. The `v0.9.6` release-candidate package is ready for
maintainer review, but it is not a release action and must not be tagged
without explicit maintainer authorization.
