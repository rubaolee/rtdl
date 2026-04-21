# Goal678: Local Total Test, Doc Audit, And Flow Audit

Status: PASS

Date: 2026-04-20

## Scope

This is the local broad gate after Goal676/677 closed the cross-engine
prepared/prepacked visibility/count optimization round.

It covers:

- full local unittest discovery;
- public command truth audit;
- public entry smoke check;
- public-doc consistency tests;
- mechanical whitespace/syntax checks;
- flow audit of the current claim boundary.

This is a local macOS gate. Linux backend evidence for OptiX, HIPRT, and Vulkan
is inherited from the goal-specific Linux reports and should be rerun on Linux
before any final release tag.

## Full Local Test

Command:

```text
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v
```

Result:

```text
Ran 1266 tests in 108.891s
OK (skipped=187)
```

Interpretation:

- The broad local Python/native surface passes.
- Optional GPU/backend tests are skipped where the corresponding local backend
  library is unavailable.
- This does not replace Linux OptiX/Vulkan/HIPRT validation.

## Public Doc And Command Audit

Public command truth audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```json
{
  "valid": true,
  "command_count": 250,
  "public_doc_count": 14
}
```

Public entry smoke:

```text
PYTHONPATH=src:. python3 scripts/goal497_public_entry_smoke_check.py
```

Result:

```json
{
  "valid": true
}
```

Focused public-doc tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal506_public_entry_v08_alignment_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal655_tutorial_example_current_main_consistency_test -v
```

Result:

```text
Ran 10 tests in 0.001s
OK
```

## Focused Optimization Tests

The focused optimization and doc command was run before the full suite:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal671_optix_prepared_anyhit_count_test \
  tests.goal674_hiprt_prepared_anyhit_2d_test \
  tests.goal675_vulkan_prepared_anyhit_2d_test \
  tests.goal506_public_entry_v08_alignment_test \
  tests.goal654_current_main_support_matrix_test \
  tests.goal655_tutorial_example_current_main_consistency_test -v
```

Result:

```text
Ran 29 tests in 0.005s
OK (skipped=7)
```

## Mechanical Checks

Whitespace:

```text
git diff --check
```

Result: clean.

Audit script syntax:

```text
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal515_public_command_truth_audit.py \
  scripts/goal497_public_entry_smoke_check.py
```

Result: clean.

## Flow Audit

The current flow is coherent:

1. Goal669 recorded cross-engine optimization lessons from Apple RT.
2. Goal670 generated OptiX/HIPRT/Vulkan optimization proposals with AI review.
3. Goals671-673 implemented and reviewed OptiX prepared/prepacked count.
4. Goal674 implemented and reviewed HIPRT prepared 2D any-hit.
5. Goal675 implemented and reviewed Vulkan prepared 2D any-hit plus packed
   rays.
6. Goal676/677 wrote the cross-engine closure report, refreshed public docs,
   and received Codex + Claude + Gemini acceptance.
7. Goal678 broad local test/doc/flow audit passed.

The public claim is consistent across the flow:

- prepared build-side state plus prepacked probe-side rays can make repeated
  visibility/count-style workloads faster;
- this is not a broad speedup claim;
- Apple scalar count does not imply full-row Apple speedup;
- GTX 1070 OptiX evidence is not RT-core evidence;
- HIPRT/Orochi CUDA evidence is not AMD GPU validation;
- Vulkan win requires prepacked rays.

## Remaining Release Gate

Before turning this current-main optimization round into a release, run a fresh
Linux backend gate that rebuilds and tests OptiX, Vulkan, and HIPRT from this
exact tree, then record that Linux gate in a release-level report.

No local blocker was found.
