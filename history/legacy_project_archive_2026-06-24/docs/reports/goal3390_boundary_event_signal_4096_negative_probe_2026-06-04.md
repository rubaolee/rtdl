# Goal3390 - Boundary-Event Signal 4096 Negative Probe

Date: 2026-06-04

Verdict: needs-more-evidence.

## Purpose

Goal3388 showed that the boundary-event tolerance signal matches exact OptiX
membership rows on 512, 1024, and 2048 chain slices from `br_county.cdb`.

Goal3390 intentionally steps the same route up to 4096 chains. This is a
negative probe: it checks whether the same first-boundary-event reconstruction
can safely become a route-promotion candidate at larger scale.

## Result

Artifact:
`docs/reports/goal3390_boundary_event_signal_4096_negative_probe_2026-06-04.json`

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit:
`ce87b13a7dad52e1b61cb1c31291319b80afbef8`

| Measure | Value |
| --- | ---: |
| Chains | 4096 |
| Shapes | 3762 |
| Candidate rows | 11431 |
| Boundary-event rows | 70458 |
| Exact rows | 11316 |
| Candidate extras before filter | 115 |
| Selected points | 103 |
| Selected candidate rows | 306 |
| Selected dropped rows | 117 |
| Filtered rows | 11314 |
| Missing exact rows | 3 |
| Extra rows | 1 |
| Match exact | false |

Failure samples:

```text
missing: (4283, 4286), (4284, 4286), (4285, 4286)
extra:   (3738, 3829)
```

## Diagnosis

The failure is not a resource failure:

- boundary-event output stayed device-resident;
- no boundary-event overflow occurred;
- candidate and boundary rows came from live OptiX device-column producers;
- the exact oracle remained evaluation-only.

The failure is semantic. The current route uses only candidate pairs plus a
first-boundary-event stream. The first-boundary-event stream is not rich enough
at 4096 chains to reconstruct exact membership by a simple `crossing_t`
tolerance rule:

- Point `3738` has one candidate extra `(3738, 3829)` but the strict-zero
  count signal did not select the point under the Goal3388 threshold.
- Points `4283`, `4284`, and `4285` have legitimate exact memberships against
  shape `4286`, but their first event has `crossing_t = 0.006651878...`, so the
  Goal3388 `1e-5` tolerance drops them.
- Loosening the rule to "keep any boundary event" keeps some false extras.
- Adding `boundary_id > 0` is still insufficient: it pulls in other false
  extras such as `(1647, 1641)` and `(2395, 2738)`.

This means the next useful primitive is not another app-shaped special case.
The generic gap is an exact, device-resident closed-shape relation stream or an
equivalent richer relation-witness primitive. A first-boundary-event stream is
useful evidence, but it is not a complete exact membership contract.

## Boundary

Goal3390 blocks route promotion for the Goal3388 signal. It does not authorize
release, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin,
RT-core speedup, true-zero-copy, or native default-route claims.

## Next Primitive Direction

The next engineering target should be a generic closed-shape relation stream
that can emit exact membership pair columns on device, or emit enough generic
relation evidence to let a partner continuation decide exact membership without
host materialization.

That primitive should remain app-agnostic:

- inputs: points, prepared closed-shape geometry, optional candidate pair filter;
- outputs: point id, shape id, relation/witness fields, device-resident status;
- no RayJoin, CDB, county, owner-face, or application vocabulary in the native
  ABI;
- explicit overflow and claim-boundary metadata;
- tests that compare against existing exact host rows but keep the oracle out
  of the signal inputs.
