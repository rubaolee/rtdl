# Goal2194 RayJoin Same-Query Adapter 2-AI Consensus

Date: 2026-05-17

Status: 2-AI consensus complete for Goal2192.

## Scope

This consensus covers the first same-query adapter step:

- `scripts/goal2192_rayjoin_same_query_stream_runner.py`
- `docs/reports/goal2192_rayjoin_same_query_stream_adapter_2026-05-17.md`
- `docs/reports/goal2192_demo_pip_query_stream_2026-05-17.json`
- `docs/reports/goal2192_demo_lsi_query_stream_2026-05-17.json`
- `docs/reports/goal2192_demo_pip_same_query_local_smoke_2026-05-17.json`
- `docs/reports/goal2192_demo_lsi_same_query_local_smoke_2026-05-17.json`
- `tests/goal2192_rayjoin_same_query_stream_adapter_test.py`

It does not cover a RayJoin-exported stream pod run, paper-scale RayJoin
reproduction, RTDL-vs-RayJoin performance claims, or v2.0 release readiness.

## Reviews

| Reviewer | File | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2192_rayjoin_same_query_stream_adapter_2026-05-17.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/goal2193_gemini_review_goal2192_rayjoin_same_query_adapter_2026-05-17.md` | `accept-with-boundary` |

## Consensus Finding

Codex and Gemini agree that Goal2192 correctly identifies the protocol gap left
after Goal2188: RayJoin internally generated query streams, while RTDL consumed
bounded CDB slices. The new `rtdl.rayjoin.same_query_stream.v1` schema and
runner are accepted as a first bridge for feeding identical PIP/LSI query
streams into RTDL.

The local demo artifacts are accepted only as consuming-side smoke evidence.
They correctly use:

- `producer: rtdl_demo_generator_not_rayjoin_cpp`
- `same_contract_with_rayjoin_query_exec: false`
- `paper_scale_perf_claim_authorized: false`
- `rtdl_beats_rayjoin_claim_authorized: false`
- `v2_0_release_authorized: false`

## Boundary

Goal2192 does not authorize:

- claiming RayJoin paper reproduction,
- claiming RTDL beats RayJoin,
- claiming broad RT-core speedup,
- claiming v2.0 release readiness,
- treating demo-generated streams as RayJoin `query_exec` streams.

## Next Step

The next required pod step is to patch the disposable RayJoin checkout so
`query_exec` exports its generated PIP/LSI query stream, then feed that stream
into `scripts/goal2192_rayjoin_same_query_stream_runner.py` and compare
RayJoin and RTDL with matched timing boundaries.

## Verdict

Goal2192 is accepted with boundary by Codex and Gemini.
