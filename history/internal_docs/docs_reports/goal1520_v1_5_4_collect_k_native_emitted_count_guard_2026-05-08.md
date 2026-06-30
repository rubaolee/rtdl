# Goal 1520: Native COLLECT_K Emitted-Count Guard

## Verdict

The Python native `COLLECT_K_BOUNDED` wrappers, polygon candidate wrappers, and
typed-host reduced-copy native envelope now fail closed when a native backend
reports `overflowed = 0` but also reports `emitted_count > capacity`. This
closes a defensive ABI boundary gap before further Embree/OptiX promotion work.

## Fixed Boundary

The affected wrapper paths are:

- `collect_native_i64_rows_with_backend_symbol(...)`
- `collect_native_i64_rows_into_prepared_output_buffer(...)`
- `collect_polygon_pair_candidates_bounded_embree(...)`
- `collect_polygon_pair_candidates_bounded_optix(...)`
- `run_native_collect_k_bounded_with_typed_host_buffers(...)`

These paths already failed closed when the native overflow flag was set.
Goal1520 adds the second required check: native emitted metadata must also be
within the caller-provided capacity before Python reads the output rows.

## Validation

Windows validation:

```text
Ran 23 tests in 0.016s
OK
```

Linux validation on `192.168.1.20`:

```text
Ran 23 tests in 0.006s
OK
```

The validation slice included the new emitted-count guard tests plus existing
native row-buffer, result-validator, zero-capacity, and generic ABI parity
guards.

Follow-up Windows validation after extending the guard to the typed-host
reduced-copy envelope:

```text
Ran 17 tests in 0.008s
OK
```

## Claim Boundary

Goal1520 is a correctness and safety hardening change at the native Python ABI
boundary. It does not authorize stable `COLLECT_K_BOUNDED` promotion, public
speedup wording, broad RTX wording, whole-app claims, true zero-copy wording, or
release action.
