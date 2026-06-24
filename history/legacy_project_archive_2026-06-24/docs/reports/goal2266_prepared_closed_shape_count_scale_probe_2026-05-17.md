# Goal2266: Prepared Closed-Shape Count Scale Probe

Status: diagnostic evidence recorded; review pending.

## Purpose

Goal2266 measures how the exact prepared closed-shape scalar count path scales
against row-return materialization when the RayJoin-exported 100,000-query PIP
stream is repeated with new query IDs.

This is a scale diagnostic, not a new RayJoin paper dataset claim.

## Environment

- Pod SSH: `root@69.30.85.202 -p 22064`
- Commit: `749158335c6a2d86832890c5d627b803a32041a7`
- GPU: NVIDIA RTX A5000, driver `570.211.01`
- Base query stream:
  `/root/goal2198_rayjoin_same_query_pod_r6/artifacts/rayjoin_pip_gen100000_stream.json`
- Transform: repeat the 100,000 RayJoin-exported queries with new IDs
- Repeats: one warmup, five timed repeats per path and scale

## Results

Artifact:
`docs/reports/goal2266_prepared_closed_shape_count_scale_probe_pod_2026-05-17.json`

| Factor | Queries | Expected count | Row-return median sec | Exact count median sec | Count / row ratio |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 100,000 | 8,686 | 0.06329208984971046 | 0.043399712070822716 | 0.6857051516844683 |
| 2 | 200,000 | 17,372 | 0.09712744504213333 | 0.07056158594787121 | 0.726484526770595 |
| 5 | 500,000 | 43,430 | 0.23066251166164875 | 0.17201292887330055 | 0.7457342228442421 |
| 10 | 1,000,000 | 86,860 | 0.4656780920922756 | 0.3518645130097866 | 0.7555960200508284 |

All row-return and exact-count outputs matched the expected repeated-stream
counts.

## Interpretation

The exact scalar count path remains faster than row-return materialization at
every tested scale. At 1,000,000 repeated queries, it is about `1.32x` faster.

The ratio trends upward as scale increases, which suggests that the remaining
cost is no longer mainly Python dictionary materialization. The count path still
downloads compact candidate rows and performs host-side exact refinement. This
reinforces the future-version item already recorded: a stronger RayJoin-style
fight likely needs generic device-resident output streams or partner-side
continuation, not just a scalar host count.

## Boundary

This report does not authorize:

- a RayJoin paper dataset claim,
- a claim that RTDL beats RayJoin,
- broad PIP speedup claims,
- v2.0 release readiness,
- or a true device-resident output-stream claim.

The repeated-query transform is useful for stress testing the RTDL runtime
contract, but it is not a substitute for reproducing the RayJoin paper's full
experimental matrix.
