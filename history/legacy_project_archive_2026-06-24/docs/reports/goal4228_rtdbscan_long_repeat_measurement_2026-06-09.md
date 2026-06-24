# Goal4228 RT-DBSCAN Long-Repeat Measurement

Date: 2026-06-09

Status: internal measurement-adequacy evidence accepted with boundary

## Purpose

Goal4225 proved the current RT-DBSCAN front door runs cleanly, but the default
scale row only repeated the prepared query three times. That was enough for
route-health evidence, but not enough to clear the one-second hot-path
measurement floor used by the current release-prep packet.

Goal4228 reruns the same promoted RT-DBSCAN route with a longer repeat count:

- mode: `optix_rt_core_grouped_stream_numba_column_signature_3d`
- dataset: `clustered3d`
- points: `65536`
- repeat: `20`
- warmup: `2`
- validation: skipped, matching the current no-validation timing row

## Result

Artifact root:
`docs/reports/goal4228_rtdbscan_long_repeat_rtx4000ada/`

| Field | Value |
| --- | ---: |
| source commit | `21d5af1d` |
| GPU | `NVIDIA RTX 4000 Ada Generation` |
| boundary policy | `single_pass_candidate_root_rebased` |
| grouped-stream continuation passes | `1` |
| repeat | `20` |
| warmup | `2` |
| median measured query sec | `0.09677839279174805` |
| total measured query sec | `1.7432705983519554` |
| one-second hot-path floor met | `true` |

## Interpretation

This closes the RT-DBSCAN measurement-floor ambiguity from Goal4225. The
default route remains the unblocked single-pass grouped stream, and the blocked
grouped route remains explicit/profile-specific per Goal4222.

This is not a new route promotion and not a public performance claim.

## Boundary

Goal4228 does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, paper-reproduction wording,
true-zero-copy wording, automatic partner selection, AMD performance wording, or
app-specific native-engine logic.
