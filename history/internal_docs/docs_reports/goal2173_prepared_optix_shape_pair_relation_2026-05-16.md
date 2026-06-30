# Goal2173 Prepared OptiX Shape-Pair Relation

Date: 2026-05-16

Status: implemented and pod-validated.

## Purpose

Goal2171 showed a real RayJoin-style overlay-seed row where both RTDL backends beat the CPU Python reference, but one-shot OptiX was still slower than Embree:

- Embree: `0.022165` sec
- one-shot OptiX: `0.025159` sec

That result pointed at a concrete design problem: the OptiX overlay relation path rebuilt or repacked right-side shape relation state on every call. Goal2173 applies the same principle that worked for LSI in Goal2163: prepare the build-side shape set once, then run repeated left-side probes against the reused OptiX state.

## What Changed

Goal2173 adds a generic prepared native surface:

- `rtdl_optix_prepare_shape_pair_relation_flags`
- `rtdl_optix_run_prepared_shape_pair_relation_flags`
- `rtdl_optix_destroy_prepared_shape_pair_relation_flags`

The implementation is app-agnostic. It prepares right-side shape refs, vertex arrays, GEOS prepared refs when available, and the OptiX custom-primitive BVH. It does not name RayJoin, county, soil, overlay policy, or any app-specific concept in the native ABI.

Python now exposes:

- `PreparedOptixShapePairRelation`
- `prepare_shape_pair_relation_flags_optix(...)`

The RayJoin public CDB runner can now select:

- `optix_prepared_overlay_seed`

## Pod Evidence

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL runner commit: `7ab56c1fe382c58f2500ce7aed98696c065d9323`

Collected artifact:

- `docs/reports/goal2173_prepared_overlay_seed_pod_2026-05-16.json`

## Result

The run used one warmup and five measured repeats.

| Case | Output rows | Embree sec | One-shot OptiX sec | Prepared OptiX sec | Prepared vs one-shot OptiX | Prepared vs Embree | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `overlay_county128_soil128` | 14,036 | 0.021841 | 0.024817 | 0.019191 | 1.293x | 1.138x | all pass |

Prepared setup time was `0.009708` sec. This is deliberately reported outside the hot repeated call timing because the prepared relation object is meant to be reused across repeated overlay probes.

## Interpretation

Goal2173 fixes the immediate Goal2171 regression shape: OptiX is no longer slower than Embree on the measured overlay-seed row when the build-side shape relation state is reused.

The key performance lesson is the same as in the LSI lane:

- RT traversal helps only after we stop making every call pay build-side setup costs
- prepared state must be a first-class generic runtime concept
- the engine should expose reusable generic shape/segment/ray state, while app policy stays in Python/partner code

This result also explains why earlier RayJoin numbers did not look like the RayJoin paper. RTDL was measuring a generic, unprepared primitive call surface against hot baselines. RayJoin-like acceleration needs prepared build-side state and bounded output shapes, even when the primitive itself is app-agnostic.

## Remaining Gaps

This goal does not close the full RayJoin gap. The next measurements still need:

- larger overlay slices
- stronger non-RT GPU spatial-prefilter baselines
- more complete end-to-end RayJoin composition
- paper-scale dataset protocols
- external review of the prepared overlay claim

## Claim Boundary

This goal authorizes:

- a narrow statement that prepared OptiX shape-pair relation is parity-clean on `overlay_county128_soil128`
- a narrow statement that prepared OptiX beats one-shot OptiX by `1.293x` on this row
- a narrow statement that prepared OptiX beats Embree by `1.138x` on this row
- using prepared build-side state as a required design pattern for RTDL v2 RayJoin-style workloads

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- claims against stronger CUDA/CuPy spatial-prefilter baselines
- claims that all overlay workloads will beat Embree without further measurement

## Verdict

Goal2173 is accepted as the first successful OptiX overlay-seed improvement after Goal2171. It converts the measured row from "OptiX slower than Embree" to "prepared OptiX faster than Embree" while preserving the app-agnostic engine boundary.
