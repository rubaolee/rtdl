# Goal 655: Tutorial And Example Current-Main Consistency

Date: 2026-04-20

Verdict: ACCEPT by Codex + Gemini Flash consensus.

## Goal

Refresh the tutorial/example-facing docs so new users see a consistent backend
story after Goal654:

- the released `v0.9.5` tag has native any-hit on OptiX, Embree, and HIPRT;
- current `main` also has native Vulkan any-hit and Apple RT
  native/native-assisted any-hit after rebuilding backend libraries;
- Apple RT any-hit is not programmable shader-level any-hit;
- `reduce_rows` remains a Python helper, not a native backend reduction.

## Files Changed

- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/tests/goal655_tutorial_example_current_main_consistency_test.py`

## Changes

- `docs/release_facing_examples.md` now says the released tag and current
  `main` have different any-hit backend boundaries, and links the current-main
  support matrix from the guided example path.
- `examples/README.md` no longer says Vulkan and Apple RT are compatibility
  projection only for any-hit; it now records the current-main native Vulkan
  path and Apple RT 3D/2D native/native-assisted paths.
- `docs/quick_tutorial.md` links the current-main support matrix near the
  capability-boundary link.
- A new regression test checks the stale compatibility-only wording does not
  return.

## Verification

Commands run from `/Users/rl2025/rtdl_python_only`:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal655_tutorial_example_current_main_consistency_test tests.goal654_current_main_support_matrix_test tests.goal646_public_front_page_doc_consistency_test tests.goal512_public_doc_smoke_audit_test -v
```

Result:

```text
Ran 13 tests in 0.013s
OK
```

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```json
{"command_count": 248, "public_doc_count": 14, "valid": true}
```

```text
git diff --check
```

Result: clean.

## Review Status

Codex local verdict: ACCEPT.

Gemini Flash verdict: ACCEPT.

- `/Users/rl2025/rtdl_python_only/docs/reports/goal655_gemini_flash_review_2026-04-20.md`

External review request:

- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL655_TUTORIAL_EXAMPLE_CURRENT_MAIN_CONSISTENCY_REVIEW_REQUEST_2026-04-20.md`
