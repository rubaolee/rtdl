# Goal 1431 v1.5.1 COLLECT_K_BOUNDED Generic I64 ABI Parity

## Verdict

ACCEPTED.

Generic i64 COLLECT_K_BOUNDED ABI parity only; not stable primitive promotion, not speedup wording, not zero-copy wording, not whole-app behavior, and not release action.

## Run Scope

- Backend: embree
- Library: `build/librtdl_embree.so`
- Symbol: `rtdl_embree_collect_k_bounded_i64`
- Row width: 2
- Capacity policy: exact fit plus fail-closed overflow
- Platform: Linux-6.17.0-20-generic-x86_64-with-glibc2.39
- Python: 3.12.3
- Git HEAD: 610e81a776079803e95030d661d28cc6bd995aa5
- Elapsed seconds: 0.004445

## Parity Outcome

- deduplicate_and_canonicalize_exact_fit: pass (status=0, emitted=2, overflowed=0, rows=[1, 10, 2, 20])
- fail_closed_overflow_no_partial_rows: pass (status=0, emitted=2, overflowed=1, rows=[0, 0])
- Failures: none
