# Phoenix V3 RTNN OptiX CUBIN Cache Evidence

Status: `rtnn_optix_cubin_cache_reduces_prepare_not_m7_wall_floor_not_met`.

The content-addressed CUBIN cache is a real generic OptiX backend improvement: on the RTX 4000 Ada POD it reduced RTNN evidence-harness execution_prepare from 3.337s to 0.564s (5.914x), cold-plus-query from 5.418s to 2.635s (2.056x), and runner wall from 6.122s to 3.431s (1.785x). It does not make the RTNN row M7. Warm-cache OptiX still loses cold-plus-query to CuPy at 0.794x and clears runner wall by only 1.098x, below the material floor.

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
m7_promotion_authorized: false
M7 rows added by this packet: 0
```

## Cache Controls

- Cache dir env: `RTDL_OPTIX_CUBIN_CACHE_DIR`
- Disable env: `RTDL_OPTIX_DISABLE_CUBIN_CACHE`
- Cache bytes captured: `241952`

## POD Result

- GPU: `NVIDIA RTX 4000 Ada Generation`
- Cold OptiX execution prepare: `3.337s`
- Warm OptiX execution prepare: `0.564s`
- Prepare reduction: `5.914x`
- Cold-plus-query reduction: `2.056x`
- Runner-wall reduction: `1.784x`
- Warm OptiX/CuPy hot-query speedup: `7.740x`
- Warm OptiX/CuPy cold-plus-query speedup: `0.794x`
- Warm OptiX/CuPy runner-wall speedup: `1.098x`

## Not-M7 Blockers

- Warm-cache OptiX/CuPy runner-wall speedup is positive but only 1.098x, below the 2.0x material floor.
- Warm-cache OptiX/CuPy cold-plus-query speedup is 0.794x, so cold-plus-query still loses.
- Input load and OptiX input_pack remain large; the cache only addresses CUBIN compilation/module preparation.
- No external Claude/Gemini review has accepted this candidate.
- This does not authorize RTNN whole-app, V2 comparison, or broad V3 speedup wording.

## Next Engine Action

Keep RTNN ranked_summary open. The next reusable work is input-pack/device-column reuse or persistent prepared-session amortization; do not tune RTNN-specific logic or publish the hot-query win as an end-to-end result.

## Forbidden Shortcuts

- Do not call 1.098x runner-wall speedup a Phoenix V3 performance win.
- Do not quote the 7.740x hot-query speedup without the warm-cache and prepared-query boundary.
- Do not claim CUBIN cache solves RTNN wall time.
- Do not promote this row to M7 without external review and a material wall-speedup result.

## Goal-Level Decision Audit

Decision: Record the generic OptiX CUBIN cache as a real blocker reduction, but keep RTNN ranked_summary out of M7 because material wall speed is still missing.

1. Was I foolish?
   No. The decision separates a reusable backend improvement from a release claim.
2. If yes, what actions made the decision foolish?
   It would be foolish to treat the 7.740x hot-query result or the 1.098x runner-wall result as a V3 win while cold-plus-query still loses.
3. Was there another path that would have avoided getting stuck on that idea?
   I could have tuned RTNN-specific code or polished docs. That would not have attacked the measured generic OptiX startup blocker.
4. Can I now try a different path that actually solves the problem?
   Use the cache result as a stepping stone and work on reusable input-pack or prepared-session amortization before asking for M7 review.
