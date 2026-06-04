# Goal3381 - Selective Owner-Face Live Route Probe

Date: 2026-06-04

Verdict: accept-with-boundary.

## Purpose

Goal3376 proved that the seven known RayJoin county-slice mismatch points can
be repaired when live OptiX candidate device columns are filtered by the CuPy
owner-face continuation.

Goal3378 then proved that a naive all-point incident-chain-length priority is
not correct enough to become a default policy.

Goal3380 added the missing generic continuation shape: filter only
caller-selected ambiguous point ids and pass every other candidate row through
unchanged.

This Goal3381 pod probe composes those pieces on the full 512-chain county
slice.

## Evidence

Pod: NVIDIA RTX A5000, driver 580.126.09

Source commit: `6ee730b9490ed727c18c6374dd2c085dc161a0f5`

Artifact:
`docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.json`

Command shape:

```bash
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so
python3 scripts/goal3381_owner_face_selective_live_route_probe.py \
  --county-cdb data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --output docs/reports/goal3381_owner_face_selective_live_route_probe_2026-06-04.json
```

## Result

| Measure | Value |
| --- | ---: |
| CDB chains / points | 512 |
| Shapes | 478 |
| Live OptiX candidate rows | 1429 |
| Live exact rows | 1417 |
| Candidate extras before filter | 12 |
| Selected ambiguity points | 7 |
| Selected candidate rows | 26 |
| Selected exact rows | 14 |
| Passthrough candidate rows | 1403 |
| Removed candidate extras | 12 |
| Filtered rows | 1417 |
| Missing exact rows | 0 |
| Extra rows | 0 |
| Full-slice match | true |

The removed extra pairs were:

```text
(522, 521), (523, 521), (538, 418), (538, 540),
(539, 418), (539, 540), (540, 535), (540, 539),
(564, 437), (564, 559), (565, 437), (565, 559)
```

## Interpretation

This is the strongest constructive owner-face result so far:

- OptiX produced the generic point/shape candidate stream for the full slice.
- The CuPy continuation repaired only the caller-supplied ambiguity set.
- Non-selected rows stayed on the fast passthrough path.
- The final row set matched the live exact OptiX oracle exactly.

This supports the v2.8 design direction: keep the native RT engine generic,
then expose explicit continuation contracts that let user/app policy repair
ambiguous boundary ownership outside the native engine.

## Boundary

This does not authorize a default route. The ambiguity set and owner-face
policy were supplied by the caller from the known Goal3328 mismatch fixture.
RTDL still does not infer those points automatically.

This does not authorize release, public speedup, RayJoin paper reproduction,
RTDL-beats-RayJoin, RT-core speedup, or true-zero-copy claims. All artifact
claim-boundary flags remain false.

The next engineering target is a generic ambiguity-set discovery policy or
front door that can decide when selective owner-face repair is required without
depending on a fixed fixture list.
