# Phoenix V3 RTNN NPZ + CUBIN Cache Evidence

Status: `rtnn_npz_cubin_cache_wall_improves_not_m7_material_floor_not_met`.

This packet records a real reusable V3 improvement, not a release win: NPZ column ingestion removes the earlier input-load wall, and the generic OptiX CUBIN cache removes most repeated compile/prepare cost. The combined route is still not M7 because full wall speed is below the material floor.

```text
release_authorized: false
public_speedup_claim_authorized: false
m7_promotion_authorized: false
```

## POD Result

- Warm OptiX/CuPy hot-query speedup: `7.784x`
- Warm OptiX/CuPy cold-plus-query speedup: `1.247x`
- Warm OptiX/CuPy runner-wall speedup: `1.328x`
- CUBIN execution-prepare reduction: `13.221x`
- CUBIN cold-plus-query reduction: `6.854x`
- CUBIN runner-wall reduction: `4.270x`

## Warm Phase Rows

| route | input load | pack/prepare | hot query | cold+query | runner wall |
|---|---:|---:|---:|---:|---:|
| RTDL OptiX | 0.025110s | 0.434345s | 0.010831s | 0.470286s | 0.844349s |
| CuPy grid | 0.014526s | 0.487670s | 0.084304s | 0.586500s | 1.121677s |

## Not M7

- Warm NPZ+CUBIN runner-wall speedup is 1.328x, below the 2.0x material floor.
- Warm NPZ+CUBIN cold-plus-query speedup is 1.247x, below the 2.0x material floor.
- The non-hot OptiX path is still about 42x the hot query, so prepare/pack/session overhead remains the blocker.
- No external Claude/Gemini review has accepted this as an M7 row.

## Remaining Blocker

- Warm OptiX non-hot path: `0.459455s`, `42.420x` the hot query.
- Warm OptiX pack+prepare: `0.434345s`.

## Next Engine Action

Keep RTNN ranked_summary open. The next reusable work is prepared-session amortization or device-column pack reuse; do not publish RTNN wall-speedup wording from a 1.328x runner-wall result.

## Forbidden Shortcuts

- Do not call 1.328x runner-wall speedup a Phoenix V3 material performance win.
- Do not quote the 7.784x hot-query speedup without the warm-cache and wall-time boundary.
- Do not promote RTNN to M7 from this packet.
- Do not claim whole-app, V2 comparison, or broad V3 speedup wording.

## Goal-Level Decision Audit

Decision: Combine the V3 NPZ input-column path with the generic OptiX CUBIN cache on the RTX POD, but keep RTNN not M7 because material wall speed is still missing.

1. Was I foolish? No. This tests two reusable V3 engine improvements together and still blocks promotion when the material floor is not met.
2. If yes, what actions made the decision foolish? It would be foolish to treat the hot-query result or the new 1.328x runner-wall result as a release-grade RTNN win.
3. Was there another path that would have avoided getting stuck on that idea? I could have stopped after the NPZ-only rerun, but that would ignore the existing generic CUBIN cache improvement and leave the blocker diagnosis incomplete.
4. Can I now try a different path that actually solves the problem? Work on reusable prepared-session amortization or input-pack/device-column reuse, or switch to another P0 generic engine item if RTNN remains below the floor.
