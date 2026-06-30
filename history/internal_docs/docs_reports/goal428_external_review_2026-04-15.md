# Goal 428 External Review

Date: 2026-04-15
Reviewer: Claude (external AI, second consensus slot)

## Is this a real RT-style Vulkan backend?

Yes. The implementation uses `VK_KHR_acceleration_structure` and
`VK_KHR_ray_tracing_pipeline` for real GPU ray-tracing traversal, not a compute
shader fallback or CPU emulation.

For the DB kernels specifically:

- `db_build_row_aabbs` converts each row into a per-row AABB primitive in
  encoded `x/y/z` space (core.cpp:2921–2942), consistent with the Goal 416
  `DbScanXYZ` and `DbGroupAggScan` contract.
- `db_collect_candidate_row_indices_vulkan` (core.cpp:2945–3043) builds a real
  BLAS over those AABBs, constructs a TLAS, dispatches a ray-tracing pipeline
  (`kDbScanRgen/Rmiss/Rint/Rahit`), and reads back a hit-word bitset.
- Exact refine happens host-side after RT candidate discovery, matching the
  bounded two-phase model in Goal 416.
- Grouped kernels (`run_db_grouped_count_vulkan`, `run_db_grouped_sum_vulkan`)
  reuse this same AABB/RT candidate path and perform bounded accumulation after
  the RT job.

The RT pipeline is not a stub. The device-level extension function pointers
(`vkCreateAccelerationStructureKHR`, `vkCmdBuildAccelerationStructuresKHR`,
`vkCmdTraceRaysKHR`, etc.) are loaded and exercised on every kernel invocation.

## Does it stay inside Goal 416?

Yes. All Goal 416 runtime ceilings are enforced at the C++ layer:

- max rows per RT job: 1 000 000 — checked in `vulkan_runtime.py`
  (`_DB_MAX_ROWS_PER_JOB`) and implicit in the AABB buffer allocation.
- max candidate rows: 250 000 — enforced by the `kDbMaxCandidateRowsPerJob`
  guard at core.cpp:3034–3036 with a runtime error on overflow.
- max distinct groups: 65 536 — enforced in the grouped kernels.
- one group key enforced by `vulkan_runtime.py` (line 436–437).
- integer-only `grouped_sum` parity is upheld: the `RtdlDbGroupedSumRow` output
  type uses `int64_t` and the Python decode path reflects this.
- prepared-mode for DB kernels is explicitly not claimed; the `run_vulkan` path
  routes DB workloads through `_run_db_vulkan` which bypasses the prepared cache.

The lowering layout (rows → AABB position on up to 3 encoded axes, probe via
query region, exact refine host-side) is textually faithful to the `DbScanXYZ`
and `DbGroupAggScan` contracts defined in Goal 416.

## Material overclaims?

None found. The report is deliberately hedged:

- Vulkan is correctly described as correctness-credible but not
  performance-leading on these bounded kernels.
- The comparison against warm-query PostgreSQL is honest: 2.5 s vs 21 ms.
- No claim is made that grouped aggregation is complete SQL; it is bounded to
  one group key and integer-compatible types.
- The `segment_polygon_hitcount` and Jaccard workloads still transparently fall
  back to the native CPU oracle with the fallback documented in `vulkan_runtime.py`
  (lines 353–379), consistent with prior goals.
- Linux authoritative result (7 tests, OK) is attested by a separate perf
  artifact with matching row counts and hashes.

One very minor observation: the perf test (`goal428_v0_7_rt_db_vulkan_perf_test`)
exercises harness structure (mocked backends, fake PostgreSQL connection) rather
than live Vulkan execution. That is appropriate for a unit-band test but means
the correctness evidence for the Vulkan path rests solely on the Linux backend
test and the Linux authoritative run. That is sufficient for this goal's stated
verification method; it is not an overclaim.

## Verdict

ACCEPT
