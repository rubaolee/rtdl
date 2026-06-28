# Call For Review: Goal4800 Kernel-First Tutorial Completion

Date: 2026-06-28

Requested reviewer: Antigravity or Claude when available.

## Review Target

Please review whether Goal4796-Goal4800 successfully repair the tutorial
program surface so users learn RTDL kernel/relation programming before V4
operator/runtime surfaces.

Primary completion audit:

- `tools/_archive/future/v4/tutorial_audits/goal4800_kernel_first_tutorial_completion_audit_2026-06-28.md`

Important files:

- `examples/tutorial_programs/README.md`
- `tests/v4_goal4800_kernel_first_tutorial_classification_test.py`
- `README.md`
- `examples/README.md`
- `tutorials/current/01_first_run.md`
- `tutorials/current/02_hello_world.md`
- `tutorials/current/04_relations_and_operators.md`
- `docs/public_documentation_map.md`
- `docs/current_v4_status.md`
- `docs/learn/source_tree_doctor.md`

## Questions

1. Are all tutorial programs now classified honestly?
2. Do core kernel-first programs actually contain real `@rt.kernel` examples?
3. Do relation-first programs explain data flow and `kernel_programming_method`
   instead of hiding behind V4 API calls?
4. Are V4-only/front-door/device-array examples clearly marked as companions,
   not first lessons?
5. Does the public learning order keep `hello_world.py`, `sorting_rows.py`, and
   relation tutorials before `v4_frontdoor_quickstart.py`?
6. Did the fix introduce any new misleading V4 performance claim, app-specific
   kernel claim, or public callback overclaim?
7. Are the validation commands sufficient for this local tutorial remediation?

## Required Verdict Labels

Please use one of:

- `approve_goal4800_kernel_first_tutorial_completion`
- `approve_with_required_amendments`
- `block_goal4800_until_fixed`

## Non-Authorization

This review request does not ask for:

- a new public release authorization;
- any V4 performance claim authorization;
- any POD benchmark authorization;
- any Tier-3 callback authorization;
- any C ABI, embedding, or true-zero-copy authorization.
