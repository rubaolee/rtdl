# Goal1450 v1.5.2 Prepared Host-Output Parity

## Verdict

NOT ACCEPTED

## Run Scope

- Primitive: `COLLECT_K_BOUNDED`
- Scope: `prepared_host_output_app_generic_i64_rows`
- Backends: `embree, optix`
- Required backends: `embree, optix`
- Case count per backend: `4`

## Parity Outcome

- embree: pass=4, fail=0, skipped=0
- optix: pass=0, fail=0, skipped=4
- Failures: none
- Required backend skips: `4`
- Required skip detail: backend=optix, case=empty_zero_capacity, reason=FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
- Required skip detail: backend=optix, case=exact_fit_two_rows_deduplicated_sorted, reason=FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
- Required skip detail: backend=optix, case=one_short_fail_closed_overflow, reason=FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
- Required skip detail: backend=optix, case=zero_capacity_positive_fail_closed_overflow, reason=FileNotFoundError: librtdl_optix not found.  Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.

## Claim Boundary

Prepared host-output parity covers app-generic row-major i64 COLLECT_K_BOUNDED execution through the existing generic native symbols only. It does not authorize true zero-copy, public speedup wording, whole-app claims, stable primitive wording, or release action.

This is not a public promotion, not a performance claim, not a zero-copy claim, and not a release action.
