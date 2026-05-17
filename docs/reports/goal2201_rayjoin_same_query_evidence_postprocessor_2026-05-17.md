# Goal2201 RayJoin Same-Query Evidence Postprocessor

Date: 2026-05-17

Status: postprocessor prepared; real evidence still requires Goal2198 pod
artifacts.

## Purpose

Goal2198 prepares the RTX pod runner that produces RayJoin same-query streams
and RTDL replay artifacts. Goal2201 adds the postprocessor that turns those raw
artifacts into a compact evidence summary.

Prepared script:

- `scripts/goal2201_rayjoin_same_query_evidence_report.py`

The Goal2198 runner now invokes this postprocessor automatically after it
writes its raw `summary.json`.

## Inputs

The postprocessor expects the Goal2198 artifact directory to contain:

- `rayjoin_lsi_grid.log`
- `rayjoin_lsi_lbvh.log`
- `rayjoin_lsi_rt.log`
- `rayjoin_pip_grid.log`
- `rayjoin_pip_lbvh.log`
- `rayjoin_pip_rt.log`
- `rtdl_lsi_same_rayjoin_stream.json`
- `rtdl_pip_same_rayjoin_stream.json`

## Outputs

The postprocessor writes:

- `evidence_summary.json`
- `evidence_report.md`

The summary includes:

- RayJoin query/build/adaptive-grouping timings parsed from logs;
- RayJoin OptiX launch counts parsed from logs;
- RayJoin intersection count where available;
- RayJoin built-in PIP check status where available;
- RTDL CPU/Embree/OptiX same-stream timing medians;
- RTDL parity status enforced by fail-closed parsing;
- derived ratios for RayJoin `rt` query phase and RTDL OptiX replay.

## Fail-Closed Checks

The parser refuses to summarize RTDL artifacts unless:

- every required RayJoin log and RTDL same-stream artifact is present;
- `query_stream_producer` is `rayjoin_query_exec_export_patch`;
- `claim_boundary.same_contract_with_rayjoin_query_exec` is true;
- every requested RTDL backend passed parity against the CPU Python reference;
- all stronger public claim flags remain false.

This prevents a demo stream, a mismatched stream, or a premature public claim
from accidentally entering a same-query evidence report.

Gemini's Goal2202 review recommended making missing RTDL artifacts fail with a
specific error instead of relying on a generic file read exception. The
postprocessor now uses explicit required-file checks for both RayJoin logs and
RTDL same-stream artifacts.

## Boundary

Goal2201 is tooling only. It does not by itself prove:

- RayJoin paper reproduction;
- RTDL beating RayJoin;
- broad RT-core speedup;
- v2.0 release readiness.

Those stronger claims require actual Goal2198 pod artifacts, an evidence
report, and external review/consensus.
