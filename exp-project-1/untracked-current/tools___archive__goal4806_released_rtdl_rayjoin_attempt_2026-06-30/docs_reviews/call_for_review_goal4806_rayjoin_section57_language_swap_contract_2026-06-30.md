# Call For Review: Goal4806 RayJoin Section 5.7 Language-Swap Contract

Date: 2026-06-30

Please review:

`docs/reports/goal4806_rayjoin_section57_language_swap_contract_2026-06-30.md`

## Review Question

Is the recorded contract correct: for a fair RayJoin Section 5.7 reproduction,
the only intended change is implementation stack
`C++/CUDA/OptiX -> Python/RTDL/Numba/RTDL-native OptiX`, while dataset,
algorithmic stages, precision policy, SoS boundary policy, output format, and
benchmark timing scope must remain unchanged?

## Specific Questions

1. Does the report correctly reflect the RayJoin paper's LSI/PIP/polygon overlay
   formulation?
2. Does it correctly capture Section 3.2 / implementation precision obligations:
   fixed-point coordinates, conservative AABBs, rationals, and SoS?
3. Does it correctly distinguish author original code from temporary Goal4806
   debug instrumentation in the author working tree?
4. Does the byte-equal County x Zipcode evidence justify saying the RTDL native
   OptiX reproduction can preserve the author workload semantics?
5. Is the performance boundary honest: correctness is proven for one full pair,
   but high-performance Section 5.7 and V4+Numba claims remain unproven?
6. Was the Numba `CUDA_ERROR_UNSUPPORTED_PTX_VERSION` issue correctly
   diagnosed as a CUDA 12.8 NVVM versus CUDA 12.4 driver mismatch?
7. Does the CUDA 12.4 NVVM repair and measured candidate probe change the
   status from `toolchain_blocked` to `candidate_measured_but_not_full_overlay`?
8. What should be the next required action to finish Goal4806: close the County
   x Zipcode slice, feed the selected candidate into the planner, or continue
   immediately to all eight Section 5.7 pairs?

## Non-Authorization

This review request does not authorize:

- public Section 5.7 high-performance claims;
- release claims for V4+Numba RayJoin;
- replacing author-code comparison with paper-table numbers;
- changing the workload after seeing results;
- treating a byte-equal correctness row as a speedup row.
