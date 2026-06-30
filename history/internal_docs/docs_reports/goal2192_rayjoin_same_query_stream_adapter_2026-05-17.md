# Goal2192 RayJoin Same-Query Stream Adapter

Date: 2026-05-17

Status: RTDL same-query consuming side implemented and locally smoke-tested;
RayJoin C++ query-export patch and RTX timing run still pending.

## Purpose

Goal2188 proved useful RTX pod evidence, but it also exposed the comparison
gap: RayJoin `query_exec` generated query points/segments internally, while
RTDL consumed bounded CDB slices. Those are adjacent experiments, not a direct
same-contract performance fight.

Goal2192 starts the same-contract lane by adding a query-stream contract that
RTDL can consume. The intended next pod step is:

1. Patch the disposable external RayJoin checkout so `query_exec` can export
   the generated PIP points or LSI segments it actually used.
2. Feed that exported stream into RTDL without regenerating it.
3. Compare RayJoin and RTDL on identical base data, identical query stream,
   matched warmup/repeat protocol, and explicit timing boundaries.

## New Script

Added:

- `scripts/goal2192_rayjoin_same_query_stream_runner.py`

The script has two commands:

| Command | Purpose |
| --- | --- |
| `materialize-demo-stream` | Produce a tiny deterministic local stream for testing the RTDL consuming side only. |
| `run-stream` | Load a same-query stream, bind it to RayJoin CDB base data, and run RTDL backends with parity checks. |

## Query Stream Schema

Schema:

- `rtdl.rayjoin.same_query_stream.v1`

Required fields:

| Field | Meaning |
| --- | --- |
| `schema` | Must be `rtdl.rayjoin.same_query_stream.v1`. |
| `producer` | Names the stream producer. Strong evidence requires `rayjoin_query_exec_export_patch`. |
| `workload` | `pip` or `lsi`. |
| `base_cdb` | RayJoin CDB file used as the build/base map. |
| `rayjoin_query_exec_flags` | The RayJoin generation flags that produced the stream. |
| `query_count` | Number of query rows. |
| `queries` | PIP point rows or LSI segment rows. |

PIP query row:

```json
{"id": 1, "x": -48.0, "y": -12.0}
```

LSI query row:

```json
{"id": 1, "x0": -48.0, "y0": -12.0, "x1": -47.9, "y1": -12.1}
```

## Local Smoke Evidence

Demo query streams:

- `docs/reports/goal2192_demo_pip_query_stream_2026-05-17.json`
- `docs/reports/goal2192_demo_lsi_query_stream_2026-05-17.json`

Local smoke artifacts:

- `docs/reports/goal2192_demo_pip_same_query_local_smoke_2026-05-17.json`
- `docs/reports/goal2192_demo_lsi_same_query_local_smoke_2026-05-17.json`

Results:

| Workload | Query count | Reference rows | Backends | Parity |
| --- | ---: | ---: | --- | --- |
| `pip` | 12 | 1 | `cpu_python_reference`, `cpu` | true |
| `lsi` | 12 | 2 | `cpu_python_reference`, `cpu` | true |

These local rows prove that RTDL can consume an external query stream for PIP
and LSI. They do not prove RayJoin same-contract timing because the stream
producer is:

- `rtdl_demo_generator_not_rayjoin_cpp`

Accordingly, every local artifact keeps:

- `same_contract_with_rayjoin_query_exec: false`
- `paper_scale_perf_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `v2_0_release_authorized: false`

## Exact RayJoin Export Requirement

The next RTX pod run should add a disposable RayJoin checkout patch that exports
the actual generated query stream after RayJoin creates it and before any mode
executes it.

For `RunPIPQuery`, export:

- `FLAGS_poly1`
- `FLAGS_query=pip`
- `FLAGS_gen_n`
- `FLAGS_gen_t`
- `FLAGS_seed`
- generated `query_points`

For `RunLSIQuery`, export:

- `FLAGS_poly1`
- `FLAGS_query=lsi`
- `FLAGS_gen_n`
- `FLAGS_gen_t`
- `FLAGS_seed`
- generated query-map edges as `{id, x0, y0, x1, y1}`

The export should not change RayJoin's algorithms. It should only serialize the
query data that RayJoin already generated. Once the producer is
`rayjoin_query_exec_export_patch`, the RTDL result artifact can set:

- `same_contract_with_rayjoin_query_exec: true`

It still must not set any public performance claim flags until reviewed.

## Engine Boundary

No RTDL native engine code was changed for Goal2192.

RTDL consumes generic:

- points and polygons for PIP,
- query segments and base segments for LSI,
- backend rows and parity contracts.

RayJoin-specific policy remains outside the engine:

- CDB interpretation,
- query stream provenance,
- RayJoin flag metadata,
- comparison/reporting.

## Verdict

Goal2192 is accepted as a first same-contract adapter step.

It is not yet RayJoin paper reproduction. It creates the missing bridge needed
for the next pod run: RTDL can now consume a query stream exported from
RayJoin, so the next performance experiment can stop comparing adjacent
protocols and start comparing identical query streams.
