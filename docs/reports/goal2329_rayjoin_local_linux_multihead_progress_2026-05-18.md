# Goal2329 RayJoin Local Linux Multi-Head Progress

Date: 2026-05-18

Status: `local-linux-smoke-complete-pod-still-needed`

## Purpose

No RTX pod was available, so this round used the local Linux validation host to
make non-sequential progress on the RayJoin benchmark application:

1. validate the pushed Goal2327 commit on Linux;
2. build the OptiX runtime in a clean validation checkout;
3. run the new prepared OptiX PIP/LSI route on local GTX 1070 smoke hardware;
4. generate deterministic same-query demo streams;
5. verify CPU / Embree / OptiX parity on those streams;
6. preserve the boundary that these artifacts are not RayJoin-paper performance
   evidence and do not authorize v2.0 release claims.

## Environment

| Item | Value |
| --- | --- |
| Host | `192.168.1.20` (`lx1`) |
| Checkout | `/home/lestat/work/rtdl_goal2327_linux_check` |
| Commit | `a83f0ff4ed381abad01d75bda4cb9cda644874e1` |
| Python | `Python 3.12.3` |
| GPU | `NVIDIA GeForce GTX 1070, 580.126.09` |
| OptiX SDK | `/home/lestat/vendor/optix-dev` |
| OptiX library | `build/librtdl_optix.so` |

The GTX 1070 host is useful for build/runtime smoke testing but is not accepted
RTX pod evidence for RayJoin performance claims.

## Linux Validation

The clean Linux checkout ran the focused contract packet:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2327_rayjoin_prepared_route_contract_test \
  tests.goal2327_rayjoin_perf_tuning_packet_test \
  tests.goal2326_public_primitive_contract_test \
  tests.goal2326_execution_report_contract_test
```

Result: `14` tests passed.

The OptiX runtime built with:

```bash
make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev
```

Result: `build/librtdl_optix.so` produced successfully.

## Fixture Prepared Route Smoke

The Goal2327 pod runner was executed locally with:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
STEP_TIMEOUT_SECONDS=300 \
WARMUPS=1 \
REPEATS=3 \
OUTPUT_DIR=docs/reports/goal2327_rayjoin_local_linux_smoke \
bash scripts/goal2327_rayjoin_pod_perf_runner.sh
```

| Workload | Mode | Rows/count | Query pack sec | Shape pack sec | Prepare sec | Query sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LSI | count | 1 | 0.000074 | n/a | 0.404530 | 0.000185 |
| PIP | rows, no materialization | 6 | 0.000011 | 0.000055 | 0.738646 | 0.000307 |

Artifacts:

- `docs/reports/goal2327_rayjoin_local_linux_smoke/summary.md`
- `docs/reports/goal2327_rayjoin_local_linux_smoke/fixture_lsi_prepared_count.json`
- `docs/reports/goal2327_rayjoin_local_linux_smoke/fixture_pip_prepared_rows_nomaterialize.json`

## Same-Query Demo Stream Replay

Because no RayJoin-exported streams were available locally, this round generated
deterministic RTDL demo streams. These are useful for RTDL consuming-side
validation, but they are not same-contract paper evidence.

### Prepared OptiX Repeated Query Path

| Workload | Queries | Output count | Prepare sec | Raw/rows median sec | Scalar count median sec | Count consistency |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| LSI | 4,096 | 230 | 0.307089 | 0.000520 | 0.000554 | true |
| PIP | 4,096 | 113 | 0.428165 | 0.000234 | 0.000209 | true |
| LSI | 65,536 | 3,393 | 0.307134 | 0.005573 | 0.005559 | true |
| PIP | 65,536 | 1,809 | 0.415392 | 0.001065 | 0.001107 | true |

The important shape is that one-time preparation is separated from repeated
query execution, and scalar count / row-count modes agree.

### All-Backend Parity On 4,096-Query Streams

| Workload | Backend | Median sec | Rows | Parity vs CPU reference |
| --- | --- | ---: | ---: | --- |
| LSI | CPU Python reference | 0.040922 | 230 | true |
| LSI | CPU compiled | 0.005627 | 230 | true |
| LSI | Embree | 0.001482 | 230 | true |
| LSI | OptiX | 0.001248 | 230 | true |
| PIP | CPU Python reference | 0.022951 | 113 | true |
| PIP | CPU compiled | 0.005236 | 113 | true |
| PIP | Embree | 0.001722 | 113 | true |
| PIP | OptiX | 0.000411 | 113 | true |

## What This Solves

- Goal2327 code is validated on Linux, not only Windows.
- The local OptiX runtime builds against the clean pushed commit.
- The prepared OptiX route executes for both RayJoin-relevant PIP and LSI.
- Phase timing, native telemetry, row/count modes, and summary generation all
  work outside the pod.
- CPU / Embree / OptiX same-query parity is intact on deterministic demo
  streams.

## What Remains Blocked

- Real RTX pod timing.
- RayJoin-exported same-query stream replay.
- Same-contract comparison against RayJoin `query_exec`.
- Any public claim that RTDL beats RayJoin.
- Any v2.0 release or broad RT-core performance claim.

The next pod round should fetch `origin/main` at or after `a83f0ff4`, build
OptiX, set `RTDL_OPTIX_LIBRARY`, provide RayJoin-exported `LSI_STREAM` and
`PIP_STREAM` when available, and run:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
STEP_TIMEOUT_SECONDS=900 \
WARMUPS=3 \
REPEATS=15 \
OUTPUT_DIR=docs/reports/goal2327_rayjoin_pod_perf \
bash scripts/goal2327_rayjoin_pod_perf_runner.sh
```

## Claim Boundary

This report is engineering progress only. It does not authorize:

- RayJoin paper reproduction claims;
- RTDL-vs-RayJoin speedup claims;
- broad RT-core speedup claims;
- true zero-copy claims;
- v2.0 release claims.
