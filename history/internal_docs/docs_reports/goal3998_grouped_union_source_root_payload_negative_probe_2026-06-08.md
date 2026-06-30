# Goal3998 Grouped-Union Source-Root Payload Negative Probe

Date: 2026-06-08

## Verdict

`reject`

Goal3998 tested a tempting generic optimization for fixed-radius grouped union: compute the source component root once in raygen, pass it as an OptiX payload, and reuse it inside the intersection program for same-root culling.

The idea is app-agnostic, but the pod evidence rejects it. A per-ray source-root snapshot is too stale for concurrent union-find. It under-culls badly, reports far more candidates to any-hit, and slows the grouped-union path.

The native experiment was reverted. No source-root payload optimization is promoted.

Artifact: `docs/reports/goal3998_grouped_union_source_root_payload_sweep_pod.json`

## Pod Setup

- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.05
- Source base: `11b02a508296ad7a87044900e64285fb1db93eab`
- Applied uncommitted source-root-payload experiment:
  - raygen computed one source-root snapshot per query ray,
  - grouped-union pipeline payload count changed from `1` to `2`,
  - intersection program reused payload root when available.
- Dataset/profile: `clustered3d`
- Radius: `0.5`
- Repeats: `3`

## Default Mode Regression

The table compares the Goal3996 accepted baseline with the Goal3998 source-root-payload experiment for the default mode: same-root culling on, direct side effects off.

| Point count | Baseline native sec | Source-root payload native sec | Ratio | Baseline same-root culled | Source-root culled | Baseline reported | Source-root reported |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4,096 | 0.005041 | 0.007424 | 1.473x slower | 3,473,551 | 2,551 | 10,346 | 3,481,346 |
| 16,384 | 0.026752 | 0.035251 | 1.318x slower | 55,743,718 | 9,868 | 26,693 | 55,760,543 |
| 65,536 | 0.289941 | 0.312867 | 1.079x slower | 891,004,699 | 349,196,979 | 1,842,395 | 543,650,115 |

## Interpretation

The source-root snapshot is safe in the narrow sense that it should under-cull rather than over-cull: a stale root can miss same-component candidates, but it should not incorrectly drop valid unions. That is not enough for performance.

The grouped-union path depends on current component roots changing during traversal. A source root captured once at ray launch becomes stale quickly in dense clustered data. The result is a huge collapse in same-root culling effectiveness:

- at `4,096` points, reported candidates jump from `10,346` to `3,481,346`;
- at `16,384` points, reported candidates jump from `26,693` to `55,760,543`;
- at `65,536` points, reported candidates jump from `1,842,395` to `543,650,115`.

This confirms that the next real primitive cannot be a simple per-ray root-cache payload. It needs a convergence-aware or partition-assisted strategy that preserves effective same-root culling while reducing candidate/root-read work.

## Boundary

This is a rejected negative probe. It does not authorize release, public speedup wording, broad RT-core speedup wording, whole-app acceleration wording, paper reproduction, true-zero-copy wording, automatic partner/backend selection, or app-specific native-engine logic.
