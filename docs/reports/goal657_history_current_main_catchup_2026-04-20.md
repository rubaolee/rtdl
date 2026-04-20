# Goal 657: History Current-Main Catch-Up

Date: 2026-04-20

Verdict: ACCEPT by Codex + Gemini Flash consensus.

## Goal

Make the post-`v0.9.5` current-main work discoverable from the public history
entry points. This addresses the same class of problem as the earlier history
gap complaint: important work should not exist only as scattered commits and
reports.

## Scope

Registered one compact catch-up history round for Goals650-656:

- Goal650 Vulkan native any-hit
- Goal651 Apple RT 3D any-hit
- Goal652 Apple RT 2D native-assisted any-hit
- Goal653 current-main Linux any-hit validation
- Goal654 current-main support matrix
- Goal655 tutorial/example boundary refresh
- Goal656 post-doc-refresh full local test gate

This is not a new release tag. The current public release remains `v0.9.5`.

## Files Changed

- `/Users/rl2025/rtdl_python_only/history/COMPLETE_HISTORY.md`
- `/Users/rl2025/rtdl_python_only/history/README.md`
- `/Users/rl2025/rtdl_python_only/history/revision_dashboard.md`
- `/Users/rl2025/rtdl_python_only/history/revision_dashboard.html`
- `/Users/rl2025/rtdl_python_only/history/revisions/2026-04-20-goal650-656-current-main-anyhit-doc-test-catchup/metadata.txt`
- `/Users/rl2025/rtdl_python_only/history/revisions/2026-04-20-goal650-656-current-main-anyhit-doc-test-catchup/project_snapshot/goal650_656_current_main_anyhit_doc_test_catchup.md`
- `/Users/rl2025/rtdl_python_only/tests/goal657_history_current_main_catchup_test.py`

## Verification

Command run from `/Users/rl2025/rtdl_python_only`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal657_history_current_main_catchup_test tests.goal648_public_release_hygiene_test -v
```

Result:

```text
Ran 5 tests in 0.001s
OK
```

```text
git diff --check
```

Result: clean.

## Boundary

The new catch-up summary states:

- current public release remains `v0.9.5`;
- current-main improvements are not retroactive `v0.9.5` tag claims;
- no broad any-hit speedup claim is made;
- Apple RT any-hit is not programmable shader-level Apple any-hit;
- `reduce_rows` remains a Python helper, not a native backend reduction.

## Review Status

Codex local verdict: ACCEPT.

Gemini Flash verdict: ACCEPT.

- `/Users/rl2025/rtdl_python_only/docs/reports/goal657_gemini_flash_review_2026-04-20.md`

External review request:

- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL657_HISTORY_CURRENT_MAIN_CATCHUP_REVIEW_REQUEST_2026-04-20.md`
