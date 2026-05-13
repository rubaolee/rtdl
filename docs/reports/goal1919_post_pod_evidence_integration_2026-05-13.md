# Goal1919 - Post-Pod Evidence Integration

Status: evidence-collected-release-still-blocked

Date: 2026-05-13

## Scope

Goal1919 records the first accepted Goal1913 pod batch after the Goal1918
fixed-radius dense-reference OOM guard. It integrates the copied RTX pod
artifacts into the local tree and fixes the Goal1911 readiness aggregator so it
can distinguish "pod evidence collected" from "v2.0 release authorized".

## Pod Evidence

- Pod commit: `c4aebb2a29744a3a78af9d3b2d4b8be957c7cd68`
- GPU: `NVIDIA RTX 2000 Ada Generation`
- Driver: `550.127.05`
- OptiX SDK: `v8.0.0`
- Goal1905 post-pod acceptance: `pass`
- Goal1916 post-pod artifact manifest: `pass`
- Goal1911 readiness: `blocked`

The copied artifacts are:

- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_512.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_2048.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1903_v2_partner_pod_batch_summary.json`
- `docs/reports/goal1905_v2_partner_pod_batch_acceptance.json`
- `docs/reports/goal1916_v2_post_pod_artifact_manifest.json`
- `docs/reports/goal1911_v2_readiness_aggregator.json`

## Timing Shape

Representative median rows from the pod:

| Workload | Row | Partner | v1.8 prepared median | v2 native/prepared median | Ratio |
| --- | ---: | --- | ---: | ---: | ---: |
| fixed-radius service coverage | 4096 | torch | 0.009101 s | 0.000250 s | 0.027x |
| fixed-radius event hotspot | 4096 | torch | 0.008084 s | 0.000169 s | 0.021x |
| road-hazard prepared reuse | 2048 | cupy | 0.004491 s | 0.001108 s | 0.247x |
| road-hazard prepared reuse | 2048 | torch | 0.004491 s | 0.001210 s | 0.269x |
| segment/polygon hitcount | 2048 | cupy | 0.002544 s | 0.001624 s | 0.638x |
| segment/polygon hitcount | 2048 | torch | 0.002544 s | 0.001231 s | 0.484x |

The 512-row segment/polygon rows remain mixed, so no broad workload speedup
claim is authorized.

## Claim Boundary

This evidence supports exact, artifact-scoped claims only. It does not
authorize:

- v2.0 release;
- package-install support;
- whole-app speedup claims;
- broad RT-core speedup claims;
- arbitrary PyTorch/CuPy acceleration claims;
- broad true-zero-copy wording beyond the measured partner-owned column paths.

Goal1911 now reports `pod_evidence_collected: true` only when required pod
artifacts exist and both Goal1905 and Goal1916 pass. It still reports
`v2_0_release_authorized: false`.

## Remaining Blockers

- Fresh Claude or Pro-class review of actual pod artifacts is still missing
  because Claude is quota-blocked in this session.
- Gemini Flash produced
  `docs/reviews/goal1912_gemini_review_goal1903_post_pod_artifacts_2026-05-13.md`
  with `accept-with-boundary`. Treat it as advisory until a Claude or
  Pro-class review exists because this is a key post-pod release gate and the
  Flash review overstates fixed-radius true-zero-copy support.
- Goal1920 records the Gemini Flash follow-up correction with
  `needs-more-evidence` until a Claude or Pro-class review is available.
- Final source-tree/package decision consensus is missing.
- Final v2.0 release consensus is missing.
- Explicit user release action is missing.
