# Goal4997: v2.14.3 Final Closeout After Goal4996

Date: 2026-07-04

## Purpose

This document closes the v2.14.3 RayJoin writer-free binary-operator line after
the post-4987 prepared/query-many work.

It supersedes the older 4985/4987 performance summaries only for the
prepared/query-many boundary.  The older fresh/cold evidence remains valid and
should not be erased:

- fresh/cold top4 writer-free route: about `4.220s`;
- repeated full route with LSI included: about `3.62-3.67s`;
- prepared/query-many writer-free route after Goal4996: stable rows around
  `0.33-0.35s`, latest measured median `0.436893s`, best measured
  `0.334875s`.

The prepared/query-many number is not a fresh one-shot overlay number and is not
an author-performance comparison.

## Architecture Boundary

v2.14.3 is still built around this principle:

> RTDL is a generic spatial dataflow system; RayJoin is an application on top of
> it.

The v2.14.3 route does not promote RayJoin overlay text formatting into RTDL
core.  It instead measures a writer-free binary operator:

```text
generic planar-map LSI pair-id columns
-> numeric columnar reprojection
-> generic device ordering
-> point-location face columns
-> app-owned descriptor carrier
-> binary downstream descriptor consumer
```

The application owns RayJoin-specific CDB choices, paper comparator labels, and
paper text-output formatting.  The performance route intentionally avoids the
paper text writer, because that writer is a sink-format cost rather than an RTDL
operator cost.

## What Changed After The Earlier Closeout

### Goal4995: no-go probes

Two cheap candidates were tested and rejected:

1. CPU/NumPy lexsort instead of device bitonic sort.
2. A single-pass run-bounds table probe.

Both were app-layer probes only.  Both were slower or unstable.  The app code
was restored to the best device-ordering route.

Important result:

- CPU lexsort median: `3.412529s`, far worse than the prepared/query-many
  route.
- Restored device route best check: `0.349843s`.

Conclusion: the current generic device ordering is imperfect, but CPU lexsort
is not the replacement.

### Goal4996: uint32 face-column carrier input fix

The grouped descriptor carrier was unnecessarily widening face-id inputs from
`uint32` to `int64` before invoking the app-layer Numba builder:

```python
point_faces_side = np.asarray(point_faces[side_id], dtype=np.int64)
midpoint_faces_side = np.asarray(midpoint_faces[side_id], dtype=np.int64)
```

Those inputs are face-id columns.  They are naturally `uint32`.  The fix keeps
the inputs as `uint32` and only writes output labels into `int64` arrays:

```python
point_faces_side = np.asarray(point_faces[side_id], dtype=np.uint32)
midpoint_faces_side = np.asarray(midpoint_faces[side_id], dtype=np.uint32)
```

This removed large host-side widening copies, especially on the side with
millions of vertex face ids.  It did not change RayJoin overlay semantics, LSI,
PIP, sort order, descriptor labels, RTDL core, or native code.

## Current Prepared/Query-Many Result

Latest top4 County x Zipcode representative run:

- artifact:
  `history/internal_docs/goal4996_uint32_face_carrier_artifacts_2026-07-04/goal4996_uint32_faces_top4.json`
- `lsi_row_count = 428322`
- `descriptor_pair_count = 15014`
- best writer-free hot time: `0.3348747044801712s`
- measured median writer-free hot time: `0.436893492937088s`

Representative stable rows:

| row | writer-free hot | LSI | sort1 | carrier total | side0 prepare | side1 prepare | side0 builder | side1 builder |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| warmup 2 | `0.345878s` | `0.003341s` | `0.126459s` | `0.101020s` | `0.000038s` | `0.000067s` | `0.018621s` | `0.073541s` |
| warmup 3 | `0.336336s` | `0.003207s` | `0.116395s` | `0.100930s` | `0.000029s` | `0.000074s` | `0.018051s` | `0.074619s` |
| measured 1 | `0.334875s` | `0.003057s` | `0.118949s` | `0.101033s` | `0.000029s` | `0.000075s` | `0.018293s` | `0.073903s` |
| measured 5 | `0.342434s` | `0.003295s` | `0.119661s` | `0.102487s` | `0.000028s` | `0.000079s` | `0.018192s` | `0.074192s` |

The stable prepared/query-many route is now roughly:

- LSI replay / pair-id columns: `~0.003s`;
- reprojection: `~0.004s`;
- sort0: `~0.03-0.04s`;
- sort1: `~0.116-0.126s`;
- grouped carrier: `~0.101-0.104s`;
- descriptor consumer: `~0.016s`;
- PIP, midpoint, and assign phases: usually `~0.04-0.07s` combined, with
  occasional POD/runtime spikes.

## Performance Evolution

| Boundary | Time | Meaning |
| --- | ---: | --- |
| Early writer-free top4 route | `7.851s` | Before exact LSI device columns / fast scaled-point packing / prepared route work |
| Fresh/cold v2.14.3 route | `4.220s` | Conservative one-shot evidence; includes LSI production and first-use setup |
| Repeated full route, LSI included | `3.62-3.67s` | Same process; still includes LSI production |
| Prepared/query-many route before Goal4996 | median about `0.3665s` | Prepared pair, writer-free binary consumer, device ordering, compiled carrier |
| Prepared/query-many route after Goal4996 | stable `0.33-0.35s`, median `0.4369s` | Carrier widening-copy removed; median still affected by runtime variance |

The honest v2.14.3 result is therefore two-part:

1. For fresh one-shot evidence, the public bounded matrix remains `~4.220s`.
2. For prepared/query-many binary-operator use, the route now has stable rows
   around `0.33-0.35s` on the top4 representative input.

Do not mix those boundaries.

## What This Does Not Claim

This closeout does not claim:

- author-performance parity;
- a measured top4 author ratio;
- that `0.33-0.35s` is a fresh one-shot overlay time;
- that paper text-output performance is solved;
- that RTDL core is free of all historical RayJoin-named implementation debt;
- that a better generic GPU ordering primitive has been built.

## Remaining Floor

The user selected not to continue with a new generic GPU ordering primitive for
v2.14.3.  That is a valid closeout decision.

The remaining stable prepared/query-many floor is:

1. generic device ordering, especially map1 sort (`~0.12s`);
2. app-layer compiled carrier builder (`~0.10s`);
3. smaller PIP/midpoint/assign and descriptor-consumer phases.

If v2.14.4 continues this line, the next meaningful work is not another
RayJoin-specific app shortcut.  It is either:

- a better generic GPU ordering / segmented ordering primitive; or
- a more general device-resident downstream operator pipeline that can be
  demonstrated on RayJoin and a non-RayJoin spatial workload.

## Validation

Local validation:

```text
py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
PYTHONPATH=src py -m unittest tests.goal4990_binary_repeat_protocol_test tests.goal4988_lsi_device_columns_direct_numba_handoff_test
```

POD validation:

```text
PYTHONPATH=src python -m unittest tests.goal4990_binary_repeat_protocol_test
```

POD top4 run produced the Goal4996 artifact listed above.

## Exit Label

`completed_v2_14_3_prepared_query_many_closeout_after_goal4996`
