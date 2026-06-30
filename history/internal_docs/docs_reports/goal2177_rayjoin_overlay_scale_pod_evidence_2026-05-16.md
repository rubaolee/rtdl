# Goal2177 RayJoin Overlay Scale Pod Evidence

Date: 2026-05-16

Status: implemented and pod-validated.

## Purpose

Goal2175 made the first larger RayJoin-style overlay row parity-clean and
showed a same-contract OptiX win over Embree on `overlay_county256_soil256`.
Goal2177 asks whether that win survives and grows at larger CDB slices.

Two new runner cases were added:

- `overlay_county384_soil384`
- `overlay_county512_soil512`

Both use the same generic RTDL overlay-seed dependency contract:

- input: left/right polygon sets
- output: `left_polygon_id`, `right_polygon_id`, `requires_lsi`, `requires_pip`
- app policy remains outside the native engine

## Pod Evidence

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts inherited from the active RayJoin pod lane:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL runner commit: `f161c8aafdfc0a469c4e23f92859b810e9f9b8be`

Collected artifacts:

- `docs/reports/goal2177_overlay384_scale_pod_2026-05-16.json`
- `docs/reports/goal2177_overlay512_scale_pod_2026-05-16.json`

Both runs used one warmup and three measured repeats. Both built a shared CPU
Python reference once, then reused the same truth rows across CPU/native-oracle,
Embree, one-shot OptiX, and prepared OptiX.

## Result

| Case | Rows | CPU/native-oracle sec | Embree sec | OptiX one-shot sec | Prepared OptiX sec | OptiX vs Embree | Prepared vs Embree | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `overlay_county384_soil384` | 130,320 | 11.283898 | 0.465292 | 0.177676 | 0.186106 | 2.619x | 2.500x | all pass |
| `overlay_county512_soil512` | 233,766 | 35.656977 | 1.188169 | 0.322171 | 0.336156 | 3.688x | 3.535x | all pass |

Reference generation cost remained separate from hot backend timing:

| Case | Shared CPU Python reference rows | Reference build sec |
| --- | ---: | ---: |
| `overlay_county384_soil384` | 130,320 | 57.616997 |
| `overlay_county512_soil512` | 233,766 | 95.760134 |

## Interpretation

The RayJoin-style overlay gap now has a clear scale trend on these CDB slices:

- `overlay_county256_soil256`: one-shot OptiX beats Embree by `1.844x`
- `overlay_county384_soil384`: one-shot OptiX beats Embree by `2.619x`
- `overlay_county512_soil512`: one-shot OptiX beats Embree by `3.688x`

This explains why earlier small/unprepared measurements did not resemble the
RayJoin paper. The RT path needs enough candidate work to amortize fixed OptiX
costs. Once the row is large enough, the same generic RTDL contract starts to
show a widening OptiX advantage over Embree.

Prepared OptiX also beats Embree at both larger sizes, but one-shot OptiX is
still faster for these current overlay rows. That means prepared state remains
important as a runtime option, especially for repeated build-side reuse, but it
should be selected by evidence and workload shape rather than by default.

## Claim Boundary

This goal authorizes:

- a narrow statement that the 384 and 512 overlay-seed rows are parity-clean
  across CPU/native-oracle, Embree, one-shot OptiX, and prepared OptiX
- a narrow statement that one-shot OptiX beats Embree by `2.619x` on
  `overlay_county384_soil384`
- a narrow statement that one-shot OptiX beats Embree by `3.688x` on
  `overlay_county512_soil512`
- a design conclusion that larger overlay-seed rows are now showing the
  expected RT acceleration trend

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- whole-app RayJoin speedup claims
- claims against stronger CUDA/CuPy spatial-prefilter baselines
- claims that prepared OptiX is always faster than one-shot OptiX

## Verdict

Goal2177 is accepted as scale evidence for the RayJoin overlay-seed lane. It
does not close the full RayJoin-paper reproduction problem, but it shows that
RTDL's generic OptiX overlay dependency primitive becomes substantially faster
than Embree as the same-contract CDB slice grows.
