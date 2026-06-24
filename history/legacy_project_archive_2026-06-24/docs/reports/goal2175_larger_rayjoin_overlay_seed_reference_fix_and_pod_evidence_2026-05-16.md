# Goal2175 Larger RayJoin Overlay Seed Reference Fix and Pod Evidence

Date: 2026-05-16

Status: implemented and pod-validated.

## Purpose

Goal2173 proved that prepared OptiX shape-pair relation could make the
`overlay_county128_soil128` row faster than Embree. The next question was
whether this held on a larger real RayJoin-style CDB slice.

The first `overlay_county256_soil256` run exposed a harness problem before it
could be used as evidence: the slow Python reference materializer rescanned all
LSI and PIP hit rows for every polygon pair. That made the reference path take
minutes, and an early diagnostic artifact reported three PIP-flag mismatches
that did not reproduce under a direct first-vertex PIP contract check.

Goal2175 fixes that reference materialization cost by precomputing pair sets:

- `lsi_pairs` for segment-intersection dependency flags
- `pip_pairs` for first-vertex containment dependency flags

This preserves the same row contract while making the reference usable for
larger correctness checks.

## Code Change

`overlay_compose_cpu(...)` now computes exact pair membership once and then
materializes rows through O(1) set lookups. The public schema is unchanged:

- `left_polygon_id`
- `right_polygon_id`
- `requires_lsi`
- `requires_pip`

The new test
`tests/goal2175_overlay_reference_pair_set_materialization_test.py` checks both
semantic preservation on LSI/PIP examples and the intended pair-set
materialization pattern.

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
- RTDL runner commit: `9a4b8ae1ef054406eeda8475a51f24ed3f225459`

Collected artifact:

- `docs/reports/goal2175_overlay_count256_shared_reference_pod_2026-05-16.json`

The current run used one warmup and three measured repeats on:

- county slice: `br_county_start0_count256.cdb`
- soil slice: `br_soil_start0_count256.cdb`
- loaded polygons: 241 left, 236 right
- emitted dependency rows: 56,876
- shared CPU Python reference rows: 56,876, built once in `27.386` sec and
  reused by CPU/native-oracle, Embree, one-shot OptiX, and prepared OptiX

## Result

| Backend | Median sec | Rows | Parity vs CPU Python reference |
| --- | ---: | ---: | --- |
| CPU/native-oracle | 2.185177 | 56,876 | pass |
| Embree | 0.134782 | 56,876 | pass |
| OptiX one-shot | 0.073110 | 56,876 | pass |
| OptiX prepared overlay seed | 0.078009 | 56,876 | pass |

Derived ratios:

| Ratio | Value |
| --- | ---: |
| CPU/native-oracle vs Embree | 16.213x |
| CPU/native-oracle vs OptiX one-shot | 29.889x |
| CPU/native-oracle vs prepared OptiX | 28.012x |
| Embree vs OptiX one-shot | 1.844x |
| Embree vs prepared OptiX | 1.728x |
| Prepared OptiX vs one-shot OptiX | 0.937x |

The important update is that the larger count256 row is now parity-clean and
OptiX is clearly faster than Embree on this exact overlay-seed dependency
contract.

## Interpretation

Goal2175 answers the immediate "why not RayJoin-like speedup?" issue more
sharply:

- Earlier larger-overlay evidence was blocked by the reference harness, not by
  the native relation result.
- Once the reference was repaired, the count256 row shows OptiX at `0.073110`
  sec versus Embree at `0.134782` sec, a `1.844x` same-contract OptiX win.
- Prepared state remains a valid design pattern, but this row shows that the
  current one-shot OptiX path can be faster at this scale. That means the
  runtime should select between one-shot and prepared paths based on workload
  shape, setup reuse, and call count rather than assuming prepared is always
  faster.

## Claim Boundary

This goal authorizes:

- a narrow statement that `overlay_county256_soil256` is parity-clean across
  CPU/native-oracle, Embree, one-shot OptiX, and prepared OptiX
- a narrow statement that one-shot OptiX beats Embree by `1.844x` on this row
- a narrow statement that prepared OptiX beats Embree by `1.728x` on this row
- using pair-set reference materialization as the required correctness harness
  for larger overlay-seed rows

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- whole-app RayJoin speedup claims
- claims against stronger CUDA/CuPy spatial-prefilter baselines
- claims that prepared OptiX is always faster than one-shot OptiX

## Verdict

Goal2175 is accepted as a larger, parity-clean RayJoin overlay-seed evidence
row. It also repairs the correctness harness so future large overlay tests
spend pod time on RTDL execution rather than avoidable Python reference
bookkeeping.
