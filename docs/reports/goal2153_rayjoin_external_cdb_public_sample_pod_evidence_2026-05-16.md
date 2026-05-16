# Goal2153 RayJoin External CDB Public-Sample Pod Evidence

Date: 2026-05-16

Status: pod evidence collected; external review pending.

## Purpose

Goal2152 added an app-level external-CDB adapter for the RayJoin v2 user program. Goal2153 validates that adapter on an NVIDIA pod with downloaded public RayJoin sample CDB files, while keeping the RTDL native engine app-agnostic.

This report is about ingestion, bounded same-contract execution, and performance-development lessons. It is not a RayJoin paper reproduction.

## Pod Environment

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`
- Rejected copied key: `~/.ssh/id_ed25519`

Runtime facts:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL commit on pod: `73e23e3559e8ef65c045275402887730e02fe6ed`
- OptiX library: `/root/rtdl_rayjoin_pod/build/librtdl_optix.so`
- OptiX generated PTX path: `RTDL_OPTIX_PTX_COMPILER=nvcc`, `RTDL_OPTIX_PTX_ARCH=compute_89`
- Embree: Ubuntu `libembree-dev`, `RTDL_EMBREE_PREFIX=/usr`

## Public Inputs

The pod downloaded the RayJoin sample files through `rtdsl.datasets.download_rayjoin_sample`:

| Source | Downloaded CDB size | Chains | Probe points | Segments | Polygons |
| --- | ---: | ---: | ---: | ---: | ---: |
| `br_county` | 12,826,522 bytes | 16,545 | 16,545 | 326,193 | 15,700 |
| `br_soil` | 9,543,616 bytes | 7,950 | 7,950 | 251,011 | 7,774 |

Full all-pair LSI/overlay products are too large for an unbounded first probe, so Goal2153 used deterministic chain-prefix CDB slices:

| Slice | Chains | Probe points | Segments | Polygons |
| --- | ---: | ---: | ---: | ---: |
| `br_county_512.cdb` | 512 | 512 | 24,880 | 481 |
| `br_soil_512.cdb` | 512 | 512 | 8,619 | 486 |
| `br_county_128.cdb` | 128 | 128 | 4,981 | 121 |
| `br_soil_128.cdb` | 128 | 128 | 2,885 | 116 |
| `br_county_64.cdb` | 64 | 64 | 2,451 | 59 |
| `br_soil_64.cdb` | 64 | 64 | 1,975 | 54 |

The slices are derived inputs, not exact RayJoin paper inputs.

## Artifacts

Collected artifacts:

- `docs/reports/goal2152_rayjoin_external_cdb_public_sample_pod_2026-05-16.json`
- `docs/reports/goal2152_rayjoin_external_cdb_public_sample_warm_pod_2026-05-16.json`

The first artifact is a cold one-shot app run. The second artifact uses one warmup and three measured repeats in one Python process; the table below uses the warm median values.

## Warm Median Results

All rows below use the same Python+RTDL v2 app and the external-CDB adapter. `OptiX vs CPU` and `OptiX vs Embree` are ratios where values above `1.0x` favor OptiX.

| Case | CPU sec | Embree sec | OptiX sec | OptiX vs CPU | OptiX vs Embree | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `pip_county512` | 0.016519 | 0.004878 | 0.008874 | 1.86x | 0.55x | all pass |
| `lsi_county64_soil64` | 0.006004 | 0.011856 | 0.006346 | 0.95x | 1.87x | all pass, zero-hit slice |
| `overlay_county128_soil128` | 0.156255 | 0.022309 | 0.025437 | 6.14x | 0.88x | all pass |
| `lsi_county64_self_positive_control` | 0.013550 | 0.015551 | 0.006928 | 1.96x | not comparable | CPU and OptiX pass; Embree mismatch |

## Interpretation

The external-CDB adapter works on public RayJoin sample data with CPU, Embree, and OptiX backends.

The warm OptiX path is strong enough to beat CPU on PIP, overlay seed, and the positive-control LSI self-join. It also beats Embree on the zero-hit LSI county/soil slice. Embree remains faster than OptiX on bounded PIP and overlay seed for these public slices, which is consistent with earlier RayJoin synthetic evidence: CPU Embree can be very good for compact 2D polygon/point work, while OptiX pays launch, data, and module warmup overhead.

The cold artifact shows large first-run OptiX costs. Those are real user costs for short one-shot scripts, but they should not be used as steady-state backend comparisons. The warm artifact records them separately and excludes them from the median table.

The `lsi_county64_self_positive_control` row deliberately joins a dataset against itself to create nonzero intersections. CPU and OptiX agree on 4,766 rows, while Embree returns 3,809 rows. This is a semantic diagnostic, not a performance win. The likely cause is degenerate same-input segment behavior: duplicate, shared-endpoint, or collinear/overlapping segment cases stress exact row semantics differently from normal cross-dataset RayJoin inputs. This needs a separate Embree LSI degeneracy audit before any self-join or topology-sensitive LSI claim.

## Claim Boundary

This goal authorizes:

- public RayJoin sample CDB ingestion through the Python app-level adapter
- bounded derived-input pod evidence for CPU, Embree, and OptiX execution
- warm steady-state evidence that OptiX can execute the bounded PIP, LSI, and overlay-seed paths on RTX 4000 Ada
- a narrow statement that OptiX beats CPU on the measured warm PIP, overlay seed, and LSI self-positive-control rows

This goal does not authorize:

- full RayJoin paper reproduction
- exact RayJoin paper-input performance claims
- broad RT-core speedup claims
- whole-app RayJoin acceleration claims
- use of the LSI self-positive-control Embree row as same-contract performance evidence
- v2.0 release authorization

## Next Work

1. Add a reusable bounded public-CDB runner so these samples can be retested without one-off pod scripting.
2. Investigate the Embree LSI self-join degeneracy mismatch with minimal duplicate/shared-endpoint/overlap fixtures.
3. Build a non-RT CUDA/CuPy baseline for PIP and LSI on the same bounded public CDB slices.
4. Find or derive bounded public slices with nonzero cross-dataset LSI hits.
5. Keep the current app-level adapter boundary: RayJoin parsing and slicing stay in Python; native engines stay app-agnostic.

## Verdict

Goal2153 is accepted as bounded public-sample pod evidence for the RayJoin v2 user app and as a useful performance/semantic diagnostic. It is not release evidence by itself.
