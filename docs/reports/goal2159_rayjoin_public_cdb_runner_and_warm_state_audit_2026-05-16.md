# Goal2159 RayJoin Public-CDB Runner And Warm-State Audit

Date: 2026-05-16

Status: reusable runner implemented; pod rerun evidence collected; external review pending.

## Purpose

Goal2157 found a bounded public RayJoin LSI slice where OptiX looked much faster than CPU and Embree. Goal2159 makes that work repeatable with a committed runner and audits the surprising warm-state sensitivity in the OptiX numbers.

## What Changed

Added:

- `scripts/goal2159_rayjoin_public_cdb_runner.py`
- `tests/goal2159_rayjoin_public_cdb_runner_test.py`

The runner can:

- download missing RayJoin public sample CDB files when requested
- materialize deterministic bounded CDB slices
- run selected RayJoin v2 workloads over CPU, Embree, and OptiX
- print progress for every warmup/repeat
- write JSON artifacts with claim-boundary flags
- run in `--dry-run` mode for lightweight local validation

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
- Embree: 4.3.0
- RTDL runner commit: `b521b1d4463575269dd7ce84b926d5116a8bd5f7`

Collected artifacts:

- `docs/reports/goal2159_rayjoin_public_cdb_runner_count192_pod_2026-05-16.json`
- `docs/reports/goal2159_rayjoin_public_cdb_runner_count128_192_pod_2026-05-16.json`

## Conservative Single-Case Runner Result

Command shape:

```bash
python3 scripts/goal2159_rayjoin_public_cdb_runner.py \
  --data-dir /root/rtdl_rayjoin_pod/data/rayjoin \
  --output docs/reports/goal2159_rayjoin_public_cdb_runner_count192_pod_2026-05-16.json \
  --cases lsi_county256_soil256_count192 \
  --backends cpu,embree,optix \
  --warmups 1 --repeats 5 --step-timeout 240
```

Result:

| Case | Rows | CPU sec | Embree sec | OptiX sec | OptiX vs CPU | OptiX vs Embree | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi_county256_soil256_count192` | 85 | 0.016228 | 0.030806 | 0.015426 | 1.05x | 2.00x | all pass |

This is the safer public-facing number because it is regenerated from one committed runner invocation with a single selected case.

## Multi-Case Warm-State Result

Command shape:

```bash
python3 scripts/goal2159_rayjoin_public_cdb_runner.py \
  --data-dir /root/rtdl_rayjoin_pod/data/rayjoin \
  --output docs/reports/goal2159_rayjoin_public_cdb_runner_count128_192_pod_2026-05-16.json \
  --cases lsi_county256_soil256_count128,lsi_county256_soil256_count192 \
  --backends cpu,embree,optix \
  --warmups 1 --repeats 5 --step-timeout 240
```

Result:

| Case | Rows | CPU sec | Embree sec | OptiX sec | OptiX vs CPU | OptiX vs Embree | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `count128` | 56 | 0.010915 | 0.022312 | 0.010379 | 1.05x | 2.15x | all pass |
| `count192_after_count128` | 85 | 0.016306 | 0.019314 | 0.003090 | 5.28x | 6.25x | all pass |

This reproduces the fast Goal2157 OptiX state, but only after another OptiX LSI case has already run in the same process.

## Interpretation

The important lesson is not "the 5x row was fake." It is more precise:

- the public-CDB nonzero LSI case is correct and repeatable
- OptiX is faster than Embree in both committed-runner protocols
- OptiX is only slightly faster than CPU in the conservative single-case protocol
- the larger 5x CPU speedup depends on a multi-case warmed OptiX state

Until the runner has an explicit warm-state protocol, public wording should use the conservative single-case result. The multi-case warm result is useful engineering signal for future persistent-session or batched-query design.

## Claim Boundary

This goal authorizes:

- a reusable bounded public-CDB RayJoin runner
- a conservative same-contract count192 LSI result where OptiX is 1.05x faster than CPU and 2.00x faster than Embree
- a separate engineering observation that multi-case warm state can make OptiX much faster on the same count192 slice

This goal does not authorize:

- full RayJoin paper reproduction
- paper-scale performance claims
- broad RT-core speedup claims
- whole-app RayJoin acceleration claims
- public use of the 5x warm-state row without an explicit warmed-session benchmark protocol
- v2.0 release authorization

## Next Work

1. Add a CUDA/CuPy non-RT baseline to the same runner.
2. Add an explicit `--session-warmup-cases` mode if we want to study persistent OptiX sessions.
3. Search larger bounded public CDB pairs that run in seconds and have more intersections.
4. Decide whether RayJoin LSI should use single-case or batched-session timing for public v2.0 evidence.

## Verdict

Goal2159 is accepted as a repeatability correction and benchmark-runner hardening step. It narrows the public performance interpretation while preserving the useful warm-state engineering lead.
