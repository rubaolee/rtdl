# Interim Check: Goal4999 Forced Device-Resident Handoff and Goals5000-5006

Date: 2026-07-04

## Why The Owner Forced This Correction

The owner objected to the phrase "not strictly full zero-copy" because it was
being used as a caveat instead of driving the next engineering step.

That objection was technically correct.

Before Goal4999, the v2.14.3 RayJoin Section 5.7 writer-free binary route had
made real progress, but it still did not satisfy the intended architecture:

```text
RTDL primitive output -> device/columnar continuation -> downstream operator
```

Goal4998 had moved the carrier/descriptor consumer toward device execution, but
the route still contained a hidden host boundary:

```text
device LSI/sort columns
  -> midpoint query points packed through host scaled-point records
  -> native directed point-location / PIP
```

That meant the route was not yet a clean device-resident operator. The owner
therefore forced the work away from language caveats and back to the actual
missing boundary.

## What Was Done In Goal4999

Goal4999 added a generic device-query input path for directed point-location:

```text
device query-point records
  -> generic native directed point-location prepare
  -> face-id device columns
```

Implemented pieces:

- Native generic ABI:
  `rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d`
- Native device query-point record:
  `RtdlDirectedSegmentDeviceQueryPoint2D`
- Python runtime method:
  `prepare_device_query_points(...)`
- Public planar-map wrapper forwarding under the existing point-location guard.
- RayJoin app CUDA kernel that generates midpoint query points on device.
- RayJoin app route using device midpoint query points in
  `--device-resident-carrier` mode.
- Regression guard:
  `tests/goal4999_device_query_point_location_handoff_test.py`

This is not a RayJoin core primitive. The core change is a generic directed
point-location input form. RayJoin owns midpoint construction and overlay
semantics at the app layer.

## POD Verification

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Important setup correction:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk-8.1
```

The POD default `/root/vendor/optix-dev` headers are OptiX 9.1 and fail this
driver with `Unsupported ABI version`. Rebuilding with the compatible OptiX 8.1
headers succeeded.

POD checks:

```text
exported symbol exists:
rtdl_optix_prepare_directed_segment_point_location_device_query_points_2d

POD unittest:
9 tests OK
```

Top4 route:

```text
--device-columnar
--bounded-exact-lsi-device-columns
--point-location-device-face-columns
--fast-scaled-point-pack
--prepared-operator-session
--device-resident-carrier
--warmup-runs 1
--repeat 5
```

Result artifact:

```text
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

Key result:

| Metric | Value |
|---|---:|
| LSI rows | 428,322 |
| Descriptor pairs | 15,014 |
| Best writer-free hot sec | 0.3266657907515764 |
| Median writer-free hot sec | 0.3295415733009577 |
| Worst writer-free hot sec | 0.3492758944630623 |
| Median downstream floor sec | 0.3297787792980671 |
| Median LSI phase sec | 0.0030824393033981323 |

Compared to Goal4998:

| Route | Best | Median |
|---|---:|---:|
| Goal4998 device carrier | 0.3312861304730177 | 0.338140819221735 |
| Goal4999 device midpoint query points | 0.3266657907515764 | 0.3295415733009577 |

Median improvement:

```text
0.338140819221735 / 0.3295415733009577 = 1.026x
```

## Effect Of The Forced Correction

The performance gain is modest. The important result is architectural:

```text
midpoint query-point host packed scaled-point boundary removed
```

The route now has measured device midpoint-query phases:

```text
midpoint_points_map0_device_query_points_sec ~= 0.0015s
midpoint_points_map1_device_query_points_sec ~= 0.0017s
```

That means this part of the pipeline is no longer:

```text
device -> host packed records -> native PIP
```

It is now:

```text
device -> device query records -> native PIP
```

This directly answers the owner's objection: the fix did not rename a caveat; it
removed a real host boundary.

## Current Remaining Floors

After Goal4999, the prepared/query-many writer-free top4 route is roughly:

```text
median writer-free hot: ~0.3295s
```

The largest remaining visible phases are:

| Phase | Approximate Time |
|---|---:|
| sort_map0 + sort_map1 | ~0.16s |
| device_resident_carrier_construction | ~0.087s |
| descriptor_pair_count_consumer | ~0.041s |
| vertex PIP total | ~0.030s |
| LSI replay phase | ~0.003s |
| midpoint query generation + PIP | small |

The next work must therefore target real floors, not demonstration plumbing.

## Claim Boundary

Authorized:

- Goal4999 removed the midpoint host packed scaled-point boundary in the
  device-resident carrier route.
- The generic directed point-location API can now accept device query-point
  records.
- The top4 prepared/query-many writer-free route improved modestly from
  ~0.3381s median to ~0.3295s median.

Not authorized:

- No author-parity claim.
- No fresh one-shot headline.
- No claim that every possible host interaction has disappeared.
- No claim that RayJoin-specific overlay semantics were promoted into RTDL core.
- No claim that sorting/carrier/consumer floors are solved.

## Goals5000-5006

### Goal5000: External Review Gate For Goal4999

Purpose:

Confirm that Goal4999 genuinely removed the midpoint host pack boundary and did
not hide a RayJoin-specific native kernel in RTDL core.

Work:

- Send `goal4999_device_midpoint_query_points_handoff_result_2026-07-04.md` and
  its artifact for review.
- Ask reviewer to inspect native ABI, wrapper exposure, lifetime ownership, POD
  evidence, and performance framing.

Verification:

- Review must confirm:
  - the device-query API is generic directed point-location input;
  - midpoint query-point generation remains app-owned;
  - POD evidence supports the narrow claim;
  - performance interpretation is not overclaimed.

Exit label:

```text
approve_goal4999_device_midpoint_query_point_handoff
```

### Goal5001: Device Run-Bound Generation

Purpose:

Remove the remaining run-bound host preparation boundary in the
`--device-resident-carrier` route.

Current issue:

The route still exposes small but real phases:

```text
device_resident_carrier_side0_run_bounds_to_device_sec
device_resident_carrier_side1_run_bounds_to_device_sec
```

Work:

- Generate run starts/lengths on device from sorted edge-id columns.
- Keep schema generic:

```text
sorted keys -> run starts / run lengths
```

- Do not encode overlay chain semantics in RTDL core.
- Use the generated run metadata in device carrier construction.

Verification:

- Structural counts unchanged:
  - `lsi_row_count = 428322`
  - `descriptor_pair_count = 15014`
- The `run_bounds_to_device` phases disappear or become zero.
- No host materialization of run-bound arrays in the device carrier path.

Exit label:

```text
completed_device_run_bounds_generation
```

### Goal5002: Ordering Primitive Decision

Purpose:

Decide the honest v2.14.3 ordering floor.

Current issue:

Sorting is now the biggest visible hot-stage cost:

```text
sort_map0_device_columnar_sec + sort_map1_device_columnar_sec ~= 0.16s
```

Work:

- Compare the current device sort against any already-existing generic GPU
  ordering primitive in the codebase.
- Do not invent a RayJoin-specific sorter.
- If no better generic option exists, record the current device sort as the
  v2.14.3 ordering floor.

Verification:

- Same structural counts.
- If an alternative sort is tried, it must be generic and byte/structure
  equivalent.
- If no-go, the report must explicitly say that sort/order is a remaining
  v2.14.3 floor rather than pretending it is solved.

Exit labels:

```text
completed_ordering_floor_current_device_sort
```

or

```text
completed_generic_ordering_primitive_improvement
```

### Goal5003: Binary Carrier Output Contract

Purpose:

Turn the current device carrier route from a count-oriented proof into a
clear binary output contract that a downstream operator can consume.

Current issue:

The route currently proves a descriptor-pair consumer count. That is useful, but
the product claim needs a reusable binary operator output contract.

Work:

- Define the binary output shape:

```text
descriptor_pair columns
optional group offsets
optional side/source tags
```

- Keep the contract generic:

```text
grouped descriptor pairs / grouped columnar records
```

- Keep RayJoin text formatting outside RTDL core.

Verification:

- The output contract is documented and app-name-free.
- A minimal reader can consume it without importing RayJoin helpers.
- The RayJoin app still produces the same descriptor count.

Exit label:

```text
completed_binary_carrier_output_contract
```

### Goal5004: Real Downstream Operator Proof

Purpose:

Prove that the writer-free binary route is valuable as a pipeline operator, not
just as an isolated benchmark.

Work:

- Attach a real downstream binary operator to the carrier output.
- The downstream operator should be generic, for example:
  - grouped count;
  - descriptor-pair filter;
  - descriptor-pair reduce;
  - group-level summary.
- It must return a small result, avoiding the paper text writer.

Verification:

- The downstream operator consumes the binary carrier output directly.
- No paper text writer participates.
- No `rayjoin_overlay` helper import.
- Result is deterministic and structurally checked.
- Report phase time for:
  - overlay binary production;
  - downstream operator;
  - final small result materialization.

Exit label:

```text
completed_writer_free_downstream_operator_proof
```

### Goal5005: Updated v2.14.3 Performance Matrix

Purpose:

Update the v2.14.3 matrix after Goals4999-5004.

Work:

- Report all routes separately:
  - fresh one-shot;
  - same-process prepared/query-many;
  - writer-free binary operator;
  - paper text writer route;
  - downstream-operator route.
- Keep cold/fresh and prepared/hot separate.
- Do not use warm-only numbers as a fresh headline.
- Do not compare top4 to an author baseline unless top4 author baseline is
  actually measured.

Verification:

- Matrix contains exact input name and scale.
- Matrix lists denominator for every ratio or says ratio not measured.
- All structural counts are included.

Exit label:

```text
completed_v2_14_3_updated_performance_matrix
```

### Goal5006: v2.14.3 Release/Staging Boundary Report

Purpose:

Close the v2.14.3 device-resident binary-operator stage cleanly.

Work:

- Summarize:
  - architecture changes;
  - generic-system boundary;
  - RayJoin app changes;
  - performance effect;
  - remaining floors;
  - non-authorized claims.
- Run public-surface leak scan.
- Run local/POD test summary.
- Separate project-state artifacts from release-surface files.

Verification:

- No internal goal/reviewer/process leaks in public user surface.
- No author-parity or hidden warm-only claim.
- No RayJoin-specific native/core primitive claim.
- All new public APIs are documented or explicitly kept internal.

Exit label:

```text
approve_v2_14_3_device_resident_binary_operator_release_staging
```

## Recommended Next Action

Proceed in order:

```text
Goal5000 -> Goal5001 -> Goal5002 -> Goal5003 -> Goal5004 -> Goal5005 -> Goal5006
```

Do not skip Goal5000. The owner forced Goal4999 because the project was at risk
of accepting caveats instead of removing host boundaries. That correction should
be externally checked before the next implementation step.
