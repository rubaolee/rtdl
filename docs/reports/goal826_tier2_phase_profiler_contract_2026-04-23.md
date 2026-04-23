# Goal826 Tier-2 Phase Profiler Contract

Date: 2026-04-23

## Purpose

Goal826 refreshes the Tier-2 service and hotspot OptiX phase profiler so its
outputs carry the same kind of machine-readable claim boundary introduced for
Tier-1 profilers in Goal825.

The affected profiler is:

- `/Users/rl2025/rtdl_python_only/scripts/goal811_spatial_optix_summary_phase_profiler.py`

## Scope

The profiler now emits:

- `schema_version: goal826_tier2_phase_contract_v1`
- `cloud_claim_contract.claim_scope`
- `cloud_claim_contract.non_claim`
- `cloud_claim_contract.required_phase_groups`
- `cloud_claim_contract.activation_status`
- `cloud_claim_contract.cloud_policy`

The required OptiX phase groups are:

- `input_build`
- `optix_prepare`
- `optix_query`
- `python_postprocess`

## App Boundaries

### service_coverage_gaps

Allowed future claim, after real RTX run and review:

- Prepared OptiX fixed-radius threshold traversal for coverage-gap compact
  summaries.

Explicit non-claims:

- Not nearest-clinic row output.
- Not a full service coverage optimizer.
- Not a whole-app RTX speedup claim.

### event_hotspot_screening

Allowed future claim, after real RTX run and review:

- Prepared OptiX fixed-radius count traversal for hotspot compact summaries.

Explicit non-claims:

- Not neighbor-row output.
- Not a full hotspot analytics system.
- Not a whole-app RTX speedup claim.

## Cloud Cost Policy

Both apps remain deferred. They must not cause a dedicated paid pod start. If
they are tested on cloud, they should be included only in one consolidated RTX
batch after local readiness passes.

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal826_tier2_phase_profiler_contract_test \
  tests.goal811_spatial_optix_summary_phase_profiler_test
```

Result:

```text
Ran 8 tests in 0.080s
OK
```

Compile check:

```text
python3 -m py_compile \
  scripts/goal811_spatial_optix_summary_phase_profiler.py \
  tests/goal826_tier2_phase_profiler_contract_test.py
```

Result: passed.

## Verdict

Goal826 is complete locally. It improves evidence quality without starting
cloud resources and without promoting Tier-2 apps into active RTX claims.
