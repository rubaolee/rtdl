# Gemini Review: Goal2177 RayJoin Overlay Scale

**Date:** 2026-05-16

**Reviewer:** Gemini Agent

## Goal 2177: RayJoin Overlay Scale

### Review Questions and Answers

1. **Verify that the two new scale cases are generic overlay-seed cases and do not add app-specific native engine behavior.**

   **Finding:** Verified.

   The report states that both scale cases use the same generic RTDL overlay-seed dependency contract: left/right polygon inputs and `left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip` outputs, with app policy outside the native engine. The runner defines `overlay_county384_soil384` and `overlay_county512_soil512` as `workload="overlay_seed"` cases and uses existing generic RTDL paths such as `county_soil_overlay_reference`, `rt.run_embree`, `rt.run_optix`, and `prepare_shape_pair_relation_flags_optix`. No app-specific native engine behavior is introduced.

2. **Verify the pod artifact numbers.**

   **Finding:** Verified.

   The reviewed artifacts match the requested numbers:

   - commit: `f161c8aafdfc0a469c4e23f92859b810e9f9b8be`
   - 384 row count: `130320`
   - 384 CPU/native-oracle median: `11.283897565677762`
   - 384 Embree median: `0.4652921035885811`
   - 384 OptiX one-shot median: `0.1776761505752802`
   - 384 prepared OptiX median: `0.18610582500696182`
   - 512 row count: `233766`
   - 512 CPU/native-oracle median: `35.65697741787881`
   - 512 Embree median: `1.1881687752902508`
   - 512 OptiX one-shot median: `0.3221710389479995`
   - 512 prepared OptiX median: `0.33615634217858315`

   All backends are parity-clean for both cases through `all_parity_vs_cpu_python_reference: true` in the JSON artifacts.

3. **Judge whether the narrow scale interpretation is valid.**

   **Finding:** Valid.

   The interpretations align with the data:

   - one-shot OptiX beats Embree by `2.619x` on 384: `0.4652921035885811 / 0.1776761505752802`, about `2.6187`
   - one-shot OptiX beats Embree by `3.688x` on 512: `1.1881687752902508 / 0.3221710389479995`, about `3.6880`
   - the OptiX-over-Embree advantage widens from the accepted Goal2175 256 row to 384 and 512: `1.844x`, `2.619x`, then `3.688x`
   - prepared OptiX remains useful as an option, but it is not the fastest path for these one-shot rows because one-shot OptiX is faster than prepared OptiX in both artifacts

4. **Verify that the report does not overclaim.**

   **Finding:** Verified.

   The report explicitly denies authorization for full RayJoin paper reproduction, broad RT-core speedup, v2.0 release authorization, whole-app RayJoin speedup, and claims against stronger CUDA/CuPy spatial-prefilter baselines. The `claim_boundary` objects in both JSON artifacts also keep those flags false.

### Verdict

`accept`
