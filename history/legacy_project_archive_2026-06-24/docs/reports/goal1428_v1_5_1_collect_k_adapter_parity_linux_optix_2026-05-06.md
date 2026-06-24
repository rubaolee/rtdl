# Goal 1416 v1.5.1 COLLECT_K_BOUNDED Native Parity

## Verdict

NOT ACCEPTED for this measured package.

Same-contract COLLECT_K_BOUNDED native candidate-row parity only; not a public primitive promotion, not a performance claim, and not a zero-copy claim.

## Run Scope

- Cases: empty_zero_capacity, exact_fit_two_rows, one_short_fail_closed_overflow, zero_capacity_positive_fail_closed_overflow
- Backends requested: optix
- Required backends: optix
- Row width: 2
- Capacity policy: exact fit plus fail-closed overflow probes
- Platform: Linux-6.17.0-20-generic-x86_64-with-glibc2.39
- Python: 3.12.3
- Git HEAD: 0bea4a23a6e105a5baca6ad2f8730eb7566d071d
- Elapsed seconds: 0.046387

## Parity Outcome

- optix: pass=0, fail=0, skipped=4
- Failures: none
- Required backend skips: empty_zero_capacity: optix skipped; exact_fit_two_rows: optix skipped; one_short_fail_closed_overflow: optix skipped; zero_capacity_positive_fail_closed_overflow: optix skipped

## Backend Details

- Case `empty_zero_capacity` reference: pass
- Case `empty_zero_capacity` optix: skipped (FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.)
- Case `exact_fit_two_rows` reference: pass
- Case `exact_fit_two_rows` optix: skipped (FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.)
- Case `one_short_fail_closed_overflow` reference: pass
- Case `one_short_fail_closed_overflow` optix: skipped (FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.)
- Case `zero_capacity_positive_fail_closed_overflow` reference: pass
- Case `zero_capacity_positive_fail_closed_overflow` optix: skipped (FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.)

## Files

- JSON artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.json`
- Markdown artifact: `docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.md`
