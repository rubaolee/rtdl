# Call For Review: Goals5464-5465 LibRTS Bounded Same-Input PIP

Please strictly review the first LibRTS PIP milestone.

## Files Under Review

```text
history/internal_docs/goal5464_5465_librts_bounded_same_input_pip_result_2026-07-10.md
Paper-reproduction-apps/librts-paper/librts_reproduction.py
Paper-reproduction-apps/librts-paper/run_same_input_pip_gate.py
Paper-reproduction-apps/librts-paper/author_patches/goal5464_spatialquerybenchmark_pip_only_CMakeLists.txt
Paper-reproduction-apps/librts-paper/author_patches/goal5464_cuda12_compat/amxtileintrin.h
Paper-reproduction-apps/librts-paper/data/fixtures/tiny_pip_polygons.wkt
Paper-reproduction-apps/librts-paper/data/fixtures/tiny_pip_points.wkt
Paper-reproduction-apps/librts-paper/data/fixtures/tiny_pip_expected.json
Paper-reproduction-apps/librts-paper/results/librts_goal5465_same_input_pip.json
tests/goal5464_librts_pip_contract_audit_test.py
tests/goal5465_librts_same_input_pip_gate_test.py
```

## Review Boundary

This is a bounded same-input correctness gate only. It is not Figure 12,
Ray-Multicast, a paper performance result, or full LibRTS reproduction.

## Questions

1. Does the author provenance correctly pin the AE, RTSpatial submodule, and
   SpatialQueryBenchmark commits rather than incorrectly using the public
   RTSpatial repository as the PIP source?
2. Does the PIP-only CMake wrapper compile the exact author PIP sources without
   reimplementing the algorithm or importing unrelated benchmark semantics?
3. Is the CUDA/GCC AMX shim a bounded build compatibility measure rather than a
   semantic patch?
4. Does the fixture genuinely distinguish exact polygon refinement from an
   MBR-only implementation (`4` exact hits versus `5` MBR candidates)?
5. Does the RTDL program use existing app-neutral language constructs
   (`traverse`, `point_in_polygon`, `emit`) with no LibRTS-specific core API?
6. Does the Linux/OptiX artifact prove polygon-refined author count `4`, RTDL count `4`, RTDL
   exact rows `4/4`, and `rt_core_accelerated=true` on the same files?
7. Is it correct to withhold author pair-row agreement because the author
   executable exposes only a count?
8. Are the author timing fields correctly limited to diagnostics with no
   performance ratio or Figure 12 claim?
9. Do the tests fail closed for malformed polygons, parser failures, count
   mismatches, and MBR-only false positives?
10. Does the milestone preserve the campaign-wide Embree exclusion and keep
    Ray-Multicast as a separate future mechanism audit?
11. Are any claim-boundary fields self-declared rather than supported by the
    committed evidence?
12. May Goals5464-5465 close as bounded same-input PIP count agreement with RTDL
    exact fixture rows, while all larger paper/performance claims remain open?

## Expected Answer Shape

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-12:
Requested verdict label:
```

Requested verdict label if approved:

```text
approve_goals5464_5465_librts_bounded_same_input_pip
```
