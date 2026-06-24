# Goal 1416 v1.5.1 COLLECT_K_BOUNDED Native Parity

## Verdict

ACCEPTED for this measured package.

Same-contract COLLECT_K_BOUNDED native candidate-row parity only; not a public primitive promotion, not a performance claim, and not a zero-copy claim.

## Run Scope

- Cases: empty_zero_capacity, exact_fit_two_rows, one_short_fail_closed_overflow, zero_capacity_positive_fail_closed_overflow
- Backends requested: optix
- Required backends: optix
- Row width: 2
- Capacity policy: exact fit plus fail-closed overflow probes
- Platform: Linux-6.5.0-41-generic-x86_64-with-glibc2.35
- Python: 3.11.10
- Git HEAD: 9813a0b7eea2d7ce1bffcb82159ea81f882f2d3c
- Elapsed seconds: 0.706756

## Parity Outcome

- optix: pass=4, fail=0, skipped=0
- Failures: none
- Required backend skips: none

## Backend Details

- Case `empty_zero_capacity` reference: pass
- Case `empty_zero_capacity` optix: pass
- Case `exact_fit_two_rows` reference: pass
- Case `exact_fit_two_rows` optix: pass
- Case `one_short_fail_closed_overflow` reference: pass
- Case `one_short_fail_closed_overflow` optix: pass
- Case `zero_capacity_positive_fail_closed_overflow` reference: pass
- Case `zero_capacity_positive_fail_closed_overflow` optix: pass

## Files

- JSON artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.json`
- Markdown artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.md`
