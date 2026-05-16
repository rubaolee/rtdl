# Gemini Review Task: Goal2110 Exact RT Hausdorff Nearest Witness

Please perform an independent read-only review of Goal2110 and write your review
to:

`docs/reviews/goal2111_gemini_review_goal2110_hausdorff_rt_nearest_witness_2026-05-15.md`

Context:

- The repo is `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`.
- Goal2110 adds a new OptiX prepared fixed-radius nearest-witness primitive:
  `rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d`.
- It wires `examples/rtdl_hausdorff_v2_function.py` method
  `rtdl_rt_nearest_witness`, which computes exact Hausdorff distance by using
  RTDL/OptiX traversal to return nearest witness rows, then recomputing the
  selected witness distances in Python double precision and reducing the final
  HD result.

Files to inspect:

- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/rtdsl/optix_runtime.py`
- `examples/rtdl_hausdorff_v2_function.py`
- `docs/reports/goal2110_hausdorff_exact_rt_nearest_witness_2026-05-15.md`
- `tests/goal2110_hausdorff_exact_rt_nearest_witness_test.py`
- `docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_512.json`
- `docs/reports/hausdorff_v2_rt_nearest_witness_local_optix_2048_warm.json`

Review questions:

1. Does Goal2110 honestly answer that the previous exact v2 Hausdorff path did
   not use RT cores, while the new `rtdl_rt_nearest_witness` path does use
   RTDL/OptiX traversal?
2. Is the new primitive generic enough for RTDL's app-agnostic engine boundary,
   or does it smuggle Hausdorff-specific logic into the native engine?
3. Does the report avoid overclaiming X-HD paper-level performance?
4. Do the validation artifacts support exact correctness versus OpenMP/CUDA/CuPy
   baselines on the tested cases?
5. What risks remain, especially around float tie-breaking, setup overhead, and
   the missing X-HD algorithmic layers?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. This should be a read-only review except for writing the review file.
