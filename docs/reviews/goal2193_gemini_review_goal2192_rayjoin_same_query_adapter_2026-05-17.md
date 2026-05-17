# Goal2193 Gemini Review: Goal2192 RayJoin Same-Query Stream Adapter

**Date:** 2026-05-17

**Reviewer:** Gemini

**Goal:** Perform a read-only review of Goal2192.

## Review Questions & Answers:

1.  **Does Goal2192 correctly identify the previous Goal2188 gap: RayJoin internally generated query streams while RTDL consumed bounded CDB slices?**
    Yes, Goal2192 explicitly states: "Goal2188 proved useful RTX pod evidence, but it also exposed the comparison gap: RayJoin `query_exec` generated query points/segments internally, while RTDL consumed bounded CDB slices. Those are adjacent experiments, not a direct same-contract performance fight." This aligns with the findings and conclusions of Goal2188 and Goal2191.

2.  **Is the new `rtdl.rayjoin.same_query_stream.v1` schema adequate as the first bridge for feeding identical PIP/LSI query streams into RTDL?**
    Yes, the schema defined in `docs/reports/goal2192_rayjoin_same_query_stream_adapter_2026-05-17.md` and implemented in `scripts/goal2192_rayjoin_same_query_stream_runner.py` (fields like `schema`, `producer`, `workload`, `base_cdb`, `rayjoin_query_exec_flags`, `query_count`, and `queries`) is adequate. It captures the necessary metadata and query data to facilitate the next steps of feeding RayJoin-exported streams into RTDL.

3.  **Does the script keep RayJoin-specific policy outside the RTDL native engine?**
    Yes, the report explicitly states under "Engine Boundary": "No RTDL native engine code was changed for Goal2192... RayJoin-specific policy remains outside the engine: CDB interpretation, query stream provenance, RayJoin flag metadata, comparison/reporting." The `scripts/goal2192_rayjoin_same_query_stream_runner.py` handles the RayJoin-specific aspects at the script level, but the RTDL core functions it calls remain generic.

4.  **Do the local demo artifacts prove only the RTDL consuming side, without overclaiming RayJoin C++ same-contract evidence?**
    Yes, the local smoke evidence clearly proves only the RTDL consuming side. The documentation explicitly notes: "These local rows prove that RTDL can consume an external query stream for PIP and LSI. They do not prove RayJoin same-contract timing because the stream producer is: `rtdl_demo_generator_not_rayjoin_cpp`." The artifacts consistently set `same_contract_with_rayjoin_query_exec: false`, `paper_scale_perf_claim_authorized: false`, and `rtdl_beats_rayjoin_claim_authorized: false`.

5.  **Are the claim boundaries correct, especially `same_contract_with_rayjoin_query_exec: false` for demo-generated streams?**
    Yes, the claim boundaries are correctly defined and applied. The local demo artifacts (e.g., `docs/reports/goal2192_demo_pip_same_query_local_smoke_2026-05-17.json`) and the script's logic (`scripts/goal2192_rayjoin_same_query_stream_runner.py`) consistently use `same_contract_with_rayjoin_query_exec: false` when the stream is not directly from a RayJoin C++ export.

6.  **Are the next pod steps clear enough: patch disposable RayJoin `query_exec` to export its generated stream, then feed that stream into RTDL?**
    Yes, the next pod steps are very clear. The "Purpose" and "Exact RayJoin Export Requirement" sections in `docs/reports/goal2192_rayjoin_same_query_stream_adapter_2026-05-17.md` precisely detail the required patching of RayJoin `query_exec` to export its generated query stream and the subsequent feeding of this stream into RTDL for a true same-contract comparison.

## Verdict

`accept-with-boundary`

**Expected Boundary:** Goal2192 should not be treated as RayJoin paper reproduction; it should be only a first same-query adapter step until a real RayJoin-exported stream is run on a pod. This aligns perfectly with the explicit claim boundaries set within the Goal2192 report itself, which clearly states that it is not yet RayJoin paper reproduction and that performance claims are not authorized until a true RayJoin-exported stream is used. The work successfully establishes the necessary bridge for future same-contract comparisons.
