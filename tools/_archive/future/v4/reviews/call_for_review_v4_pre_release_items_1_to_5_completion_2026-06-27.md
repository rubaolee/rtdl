# Call For Review: V4 Pre-Release Items 1-5 Completion

Date: 2026-06-27

Requested reviewer: Antigravity

Requested verdict labels:

- `approve_v4_pre_release_items_1_to_5_complete`
- `approve_with_required_fixes`
- `block_v4_release_until_items_fixed`

## Context

The release owner decided that the following five items must be completed
before the V4.0.0 public tag:

1. Fresh release recheck: clean checkout, quickstart, tutorials, wheel smoke,
   GitHub/README cleanliness.
2. Final release notes: user-facing page plus engineering summary, 10-app
   matrix, claim boundaries.
3. External-debt consolidation: record the current external approvals and issue
   a final pre-release packet.
4. UX polish: benchmark app recipe examples, operator catalog API reference,
   partner choice tutorial.
5. CI/gates: clean-checkout gate and evidence artifact tracking gate, especially
   `.log` files ignored by `.gitignore`.

Claude is unavailable until tomorrow, so this packet requests Antigravity as
the active external reviewer for this pre-release step.

## Files To Inspect

Completion record:

- `future/v4/v4_goal4779_pre_release_items_1_to_5_completion_2026-06-27.md`

Public docs:

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/v4_release_notes.md`
- `docs/v4_engineering_summary.md`
- `docs/app_level_benchmark_summary.md`
- `docs/public_documentation_map.md`
- `docs/learn/README.md`
- `docs/learn/operator_catalog.md`
- `docs/learn/partner_choice.md`
- `docs/learn/performance_wording.md`
- `tutorials/current/README.md`
- `tutorials/current/06_benchmark_apps.md`
- `tutorials/current/07_partner_choice.md`
- `examples/v4/benchmark_app_recipes.py`

Gates:

- `scripts/v4_universe_audit.py`
- `scripts/v4_release_clean_checkout_gate.py`
- `tests/v4_goal4640_public_docs_cleanup_test.py`
- `tests/v4_release_clean_checkout_gate_test.py`

## Local Result To Verify

```text
py -3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_release_clean_checkout_gate_test
Ran 16 tests in 34.803s
OK
```

## Questions

1. Are items 1-5 now implemented as pre-release requirements rather than
   postponed work?
2. Are the user-facing docs clean, current-only, and free of internal process
   language?
3. Do the tutorials and benchmark recipes teach users how to construct the V4
   app patterns rather than dumping internal release-defense wording?
4. Is the partner-choice path understandable and bounded?
5. Does the new clean-checkout gate actually catch missing or untracked release
   artifacts?
6. Does the gate specifically protect `.log` evidence files that would normally
   be ignored?
7. Is any public wording still too broad, especially around all-app speedup,
   Tier-3 callbacks, raw OptiX callbacks, CuPy, true-zero-copy, or embedding?
8. Do you authorize proceeding from this pre-release hardening step to final
   clean-tree/Linux/tag validation?

## Non-Authorization

This packet does not authorize broad V4 speedup claims, all-app speedup claims,
public true-zero-copy, Tier-3 callback/PTX support, raw OptiX callbacks, C
ABI/embedding, non-Python host bindings, broad CuPy performance wording, or a
new V4-over-V3 Barnes-Hut speed claim.

