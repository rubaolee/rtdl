# Goal2978 Primitive-First v2.5 Closeout Policy

Date: 2026-06-01

Status: **accept-with-boundary / not release-authorizing**

## Purpose

Goal2978 ingests the Claude v2.5 closeout roadmap into executable policy. The
important correction is that v2.5 is not honestly described as "Triton-first"
anymore. After Goal2896 and the later packet evidence, the correct v2.5
closeout rule is:

```text
Use a fused generic native RTDL primitive when it exactly expresses the work.
Use partner continuation only for unfused work or explicit app choice.
Choose the partner by same-contract evidence; never auto-select Triton.
```

This is a policy hardening goal, not a performance run and not a release packet.

## Code Changes

Updated:

- `src/rtdsl/v2_5_execution_path_policy.py`
- `src/rtdsl/v2_5_partner_selection_guidance.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `src/rtdsl/__init__.py`

Added:

- `tests/goal2978_primitive_first_v2_5_closeout_policy_test.py`

New machine-readable surface:

- `V2_5_PRIMITIVE_FIRST_SELECTION_DOCTRINE_VERSION`
- `v2_5_primitive_first_selection_doctrine()`
- `validate_v2_5_primitive_first_selection_doctrine()`

The doctrine explicitly records:

- primitive-first native RTDL is the fast path when a fused generic primitive
  exactly expresses the continuation;
- partner continuation is reserved for unfused work or explicit app choice;
- partner choice requires same-contract evidence;
- Tier B is a coverage/unfused-continuation category, not a Triton performance
  category;
- hidden dispatch, automatic Triton selection, automatic partner selection,
  release readiness, public speedup wording, broad RT-core wording, whole-app
  speedup wording, and true-zero-copy wording remain blocked.

## Documentation Changes

Updated:

- `docs/current_architecture.md`
- `docs/current_main_support_matrix.md`
- `docs/partner_acceleration_boundaries.md`

The learner-facing current architecture and support matrix no longer present
v2.5 as a Triton-default design. `partner_acceleration_boundaries.md` keeps the
older historical "Triton-first" planning text for auditability, but it now has
a Post-Goal2978 closeout correction saying that the primitive-first doctrine
supersedes that wording for new v2.5 work.

## Boundary

Still not authorized:

- v2.5 release;
- public speedup wording;
- whole-app speedup wording;
- broad RT-core speedup wording;
- true zero-copy wording;
- automatic Triton selection;
- package-install claims;
- app-specific native engine behavior.

This goal does not solve the Goal2977 second-architecture packet gap. Barnes-Hut
still needs a canonical packet decision for the 8192-body Embree CPU baseline
bottleneck before we can treat the RTX 4000 Ada packet as clean 7/7 release
evidence.

## Validation

Local validation:

- `py -3 -m py_compile src\rtdsl\v2_5_execution_path_policy.py src\rtdsl\v2_5_partner_selection_guidance.py src\rtdsl\v2_5_triton_app_migration.py src\rtdsl\__init__.py tests\goal2978_primitive_first_v2_5_closeout_policy_test.py`
- `PYTHONPATH=src;. py -3 -m unittest tests.goal2978_primitive_first_v2_5_closeout_policy_test tests.goal2843_v2_5_execution_path_policy_test tests.goal2782_v2_5_partner_selection_guidance_test tests.goal2783_v2_5_app_migration_selection_guidance_test tests.goal2795_v2_5_tier_label_reconciliation_test tests.goal2900_v2_5_stale_strategy_wording_guard_test`

Verdict: **accept-with-boundary**. The v2.5 closeout doctrine is now explicit
and test-covered, but it does not release v2.5.
