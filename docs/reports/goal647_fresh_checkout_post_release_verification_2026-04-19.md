# Goal647 Fresh Checkout Post-Release Verification

Date: 2026-04-19

Verdict: ACCEPT with Codex, Claude, and Gemini Flash consensus.

## Scope

This goal verifies that a user-facing fresh checkout can locate the released
`v0.9.5` tag, run the portable public examples, pass the release-package
checks, and pass the public command truth audit. It also verifies that current
`main` includes the post-release front-page documentation refresh from Goal646.

This is not a replacement for the full pre-release native backend matrix. It is
a fresh-checkout packaging and public-documentation verification gate.

## Fresh Checkout

- Fresh clone path: `/tmp/rtdl_goal647_mnpct0/rtdl`
- Clone command source: `https://github.com/rubaolee/rtdl.git`
- Remote `main` commit: `0c4d8332c19e1af9de736376a45a143677d0899f`
- `v0.9.5` tag target: `a8365ff49b21990b79ae91b0b4c2e3aefbeed155`
- Python: `Python 3.14.0`

## Released Tag Checks

Checkout:

```text
git checkout v0.9.5
HEAD is now at a8365ff Release v0.9.5 any-hit visibility and reduce rows
```

Portable public examples executed successfully:

```text
PYTHONPATH=src:. python3 examples/rtdl_hello_world.py
PYTHONPATH=src:. python3 examples/rtdl_ray_triangle_any_hit.py
PYTHONPATH=src:. python3 examples/rtdl_visibility_rows.py
PYTHONPATH=src:. python3 examples/rtdl_reduce_rows.py
```

Observed results:

- `rtdl_hello_world.py` printed `hello, world`.
- `rtdl_ray_triangle_any_hit.py` reported `parity: true`.
- `rtdl_visibility_rows.py` emitted observer-target `visible` rows.
- `rtdl_reduce_rows.py` emitted grouped count, max, and any-style reductions
  while preserving the documented boundary that `reduce_rows` is a Python
  standard-library helper, not a native RT backend reduction.

Release-package and public-doc tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal532_v0_8_release_authorization_test -v
```

Result:

```text
Ran 8 tests in 0.021s
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

## Current Main Checks

Checkout:

```text
git checkout main
0c4d8332c19e1af9de736376a45a143677d0899f
```

Public front-page, release-package, and public command tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal645_v0_9_5_release_package_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal532_v0_8_release_authorization_test -v
```

Result:

```text
Ran 11 tests in 0.020s
OK
```

Public command truth audit:

```text
PYTHONPATH=src:. python3 scripts/goal515_public_command_truth_audit.py
```

Result:

```json
{
  "classification_counts": {
    "linux_gpu_backend_gated": 33,
    "linux_postgresql_gated": 1,
    "optional_native_backend_gated": 44,
    "portable_python_cpu": 163,
    "visual_demo_or_optional_artifact": 7
  },
  "command_count": 248,
  "public_doc_count": 14,
  "valid": true
}
```

Whitespace check:

```text
git diff --check
```

Result: no output, no failure.

## Findings

- The released `v0.9.5` tag is present and resolves to the intended release
  commit.
- The current remote `main` contains the Goal646 public front-page refresh after
  the `v0.9.5` tag.
- The released tag is runnable from a fresh checkout for the portable examples
  that a new user can run without native backend setup.
- The public command truth audit remains valid on both the released tag and
  current `main`.
- No stale release-control wording was found by the Goal645/Goal646 public-doc
  checks.

## Limits

- This check did not rebuild Linux native backend libraries from the fresh
  checkout.
- This check did not rerun the full native performance matrix; that evidence is
  covered by the existing v0.9.5 pre-release reports.
- The `v0.9.5` tag intentionally does not include the Goal646 post-release
  front-page cleanup commit; current `main` does include it.

## Codex Verdict

Goal647 is accepted from Codex's side. The fresh checkout validates both the
released tag and current public-facing `main` state for the intended packaging
and documentation gate.

## External AI Reviews

- Claude review: `/Users/rl2025/rtdl_python_only/docs/reports/goal647_claude_review_2026-04-19.md`
- Gemini Flash review: `/Users/rl2025/rtdl_python_only/docs/reports/goal647_gemini_flash_review_2026-04-19.md`

Both external reviews returned `ACCEPT`. Claude explicitly checked the tag hash,
current `main` hash, public examples, unit-test counts, command audit, whitespace
check, and declared scope limits. Gemini Flash accepted the provided
fresh-checkout evidence and public-use scope.
