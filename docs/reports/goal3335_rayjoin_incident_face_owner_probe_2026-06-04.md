# Goal3335: RayJoin Incident-Face Owner Probe

Date: 2026-06-04

Status: diagnostic evidence. This does not authorize release, public speedup, RayJoin paper reproduction, RT-core speedup, true zero-copy, or RTDL-beats-RayJoin claims.

## Purpose

Goal3333 showed that the owner face needed by Goal3330 is not simply the probe chain's left or right face. Goal3335 checks whether the owner face is at least present in the local incident topology around the probe coordinate.

It is present for all seven known mismatching points, but it is not uniquely determined by a simple face-frequency rule.

## Pod Evidence

Artifact:

- `docs/reports/goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json`

Pod commit:

- `83d1c8c5`

Method:

- Load `br_county_start256_count512.cdb`.
- For each known mismatching point id, inspect the first probe coordinate used by `chains_to_probe_points(...)`.
- Collect all CDB chains incident to that coordinate.
- Count left/right face ids from those incident chains.

## Result

| Point ID | Owner Face Needed | Endpoint Incident Face Frequencies |
| ---: | ---: | --- |
| 522 | 248 | `221:2, 247:2, 248:2` |
| 523 | 248 | `221:2, 247:2, 248:2` |
| 538 | 217 | `217:2, 228:2, 253:2` |
| 539 | 217 | `217:2, 228:2, 253:2` |
| 540 | 212 | `212:2, 228:2, 253:2` |
| 564 | 187 | `187:2, 262:2, 271:2` |
| 565 | 187 | `187:2, 262:2, 271:2` |

Summary:

- Owner face present in all-vertex incident faces: 7/7
- Owner face present in endpoint incident faces: 7/7
- Simple maximum-frequency rule: insufficient, because all shown face candidates tie.

## Interpretation

This is constructive but bounded:

- The required ownership signal is available in local topology.
- A trivial left/right chain policy is insufficient.
- A trivial incident-face frequency policy is also insufficient.
- The next serious step is a deterministic, generic vertex/face ownership derivation contract that can break these ties without app-specific RayJoin logic in the native engine.

That future derivation contract should remain app/data-layer or generic topology-layer work. The native engine can consume owner-face columns once they are explicit; it must not guess benchmark semantics.
