# Call For Review: Goal5508 LibRTS Generic Float32-degenerate AABB Validity Fix

## Review target

Please strictly review Goal5508 as a generic RTDL native correction, not as a
LibRTS app result. The implementation is in
`src/native/optix/rtdl_optix_workloads.cpp`; the app-owned diagnosis and gate
are under `Paper-reproduction-apps/librts-paper`.

## Decision requested

Approve or reject the claim:

```text
Goal5508 generic_float32_degenerate_indexed_aabb_validity_fix_completed
```

The bounded claim is that two previously disagreeing official range-intersects
prefix counts now match the pinned author after a generic native fix:

```text
parks_Europe: author 34,240,217 == fixed RTDL 34,240,217
lakes_bz2:    author 34,581,812 == fixed RTDL 34,581,812
```

The isolated four-record invalid subsets return `0` for both author and fixed
RTDL. Pre-fix RTDL returned `27` and `5,005`, exactly the two full-prefix
excesses.

## Evidence packet

```text
history/internal_docs/goal5508_librts_generic_float32_degenerate_aabb_validity_fix_result_2026-07-12.md
Paper-reproduction-apps/librts-paper/results/goal5508_generic_float32_degenerate_aabb_validity_fix_gate.json
Paper-reproduction-apps/librts-paper/results/goal5508_official_parks_Europe_250k_fixed.json
Paper-reproduction-apps/librts-paper/results/goal5508_official_lakes_bz2_250k_fixed.json
Paper-reproduction-apps/librts-paper/results/goal5508_parks_degenerate_fixed2.json
Paper-reproduction-apps/librts-paper/results/goal5508_lakes_degenerate_fixed2.json
Paper-reproduction-apps/librts-paper/results/goal5508_librtdl_optix.so
tests/goal5508_librts_generic_float32_degenerate_aabb_validity_fix_test.py
```

## Questions for review

1. Does the source audit support the diagnosis that four records per prefix
   become non-strict only after the author's float32 conversion?
2. Do the author and RTDL parser MBR fingerprints and input SHA-256 values
   establish that this is not a WKT/input mismatch?
3. Does the four-record subset reproduce the complete pre-fix excess for both
   official prefixes?
4. Does the author subset result of zero provide sufficient source/runtime
   evidence for the invalid-indexed-envelope behavior, without claiming the
   author is globally correct?
5. Is the kernel validity guard generic and app-neutral, with no LibRTS,
   RTSpatial, paper, or author identity in RTDL core?
6. Is the `prim` versus `qidx` indexed-record selection correct for forward
   and backward intersection passes?
7. Do the clean POD fixed-prefix results match the author on identical files,
   and are the source/library hashes sufficient to identify the build?
8. Does the local 38-test regression result provide adequate focused coverage?
9. Is the claim boundary correct: two-prefix count correction only, with no
   complete archive matrix, pair-row equality, performance ratio, paper
   reproduction, native parity, or Embree claim?
10. Are the remaining 39 exact range-intersects archive pairs and author
    pair-row limitations correctly left as separate future scope?

## Forbidden conclusions

Do not convert this packet into any of the following:

- complete official range-intersects matrix;
- official pair-row equality;
- Figure 6 or full-paper reproduction;
- author algorithm or performance parity;
- whole-program speedup;
- LibRTS-specific native primitive;
- Embree evidence.

## Expected answer shape

```text
Verdict: approve / revise / reject
Blocking findings: ...
Required amendments: ...
Non-blocking notes: ...
Answers to questions 1-10: ...
Requested verdict label: ...
```
