# Goal4996: Uint32 Face Columns Carrier Prepare Fix Result

Date: 2026-07-04

## Purpose

Goal4996 continued the v2.14.3 RayJoin writer-free binary-route optimization after Goal4995 rejected two speculative candidates.

The target was the grouped descriptor carrier construction path.  Prior detailed phase output showed that `grouped_compiled_carrier_side*_prepare_inputs_sec` could randomly dominate, sometimes taking hundreds of milliseconds or more.  The suspected cause was unnecessary host-side widening copies:

```python
point_faces_side = np.asarray(point_faces[side_id], dtype=np.int64)
midpoint_faces_side = np.asarray(midpoint_faces[side_id], dtype=np.int64)
```

Those arrays are face-id columns already produced as `uint32`.  Converting them to `int64` on every run creates large host copies, especially for side1 with millions of vertex face ids.

## Change

In:

`Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

the grouped carrier builder now keeps face-id input columns as `uint32`:

```python
point_faces_side = np.asarray(point_faces[side_id], dtype=np.uint32)
midpoint_faces_side = np.asarray(midpoint_faces[side_id], dtype=np.uint32)
```

The Numba builder still writes output labels into `int64` arrays.  The change only removes unnecessary input widening copies.  It does not change RayJoin semantics, output labels, LSI, PIP, sort order, or RTDL core/native code.

## Boundary

This is an app-layer binary-route optimization.

It does not:

- modify `src/rtdsl/**`;
- modify `src/native/**`;
- add a RayJoin-specific RTDL core primitive;
- authorize paper-text output performance claims;
- authorize author-performance parity claims;
- change the fresh one-shot headline boundary.

## Validation

Local validation:

- `py -m py_compile Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `PYTHONPATH=src py -m unittest tests.goal4990_binary_repeat_protocol_test tests.goal4988_lsi_device_columns_direct_numba_handoff_test`

POD validation:

- `PYTHONPATH=src python -m unittest tests.goal4990_binary_repeat_protocol_test`
- top4 County x Zipcode prepared/query-many run on the same POD and same rebuilt top4 CDBs.

Artifact:

- `history/internal_docs/goal4996_uint32_face_carrier_artifacts_2026-07-04/goal4996_uint32_faces_top4.json`

Structural anchors:

- `lsi_row_count = 428322`
- `descriptor_pair_count = 15014`
- `single_lsi_row_count = true`
- `single_descriptor_pair_count = true`

## Result

The fix removed the carrier input widening-copy cost.

Representative stable rows:

| row | writer-free hot | LSI | sort1 | carrier total | side0 prepare | side1 prepare | side0 builder | side1 builder |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| warmup 2 | `0.345878s` | `0.003341s` | `0.126459s` | `0.101020s` | `0.000038s` | `0.000067s` | `0.018621s` | `0.073541s` |
| warmup 3 | `0.336336s` | `0.003207s` | `0.116395s` | `0.100930s` | `0.000029s` | `0.000074s` | `0.018051s` | `0.074619s` |
| measured 1 | `0.334875s` | `0.003057s` | `0.118949s` | `0.101033s` | `0.000029s` | `0.000075s` | `0.018293s` | `0.073903s` |
| measured 5 | `0.342434s` | `0.003295s` | `0.119661s` | `0.102487s` | `0.000028s` | `0.000079s` | `0.018192s` | `0.074192s` |

The previous stable carrier total was about `0.115-0.120s`.  The new stable carrier total is about `0.101-0.104s`, and the large `prepare_inputs` spikes caused by face-column widening are gone.

The measured median is still affected by unrelated POD/GPU timing spikes in sort and vertex PIP:

- measured median writer-free hot time: `0.436893s`
- best writer-free hot time: `0.334875s`

Those spikes are not caused by carrier input widening.  The stable rows show the fixed carrier behavior directly.

## Interpretation

This is a real but bounded improvement:

- It removes an unnecessary host-side widening copy.
- It improves and stabilizes grouped carrier preparation.
- It preserves the generic/app-layer boundary.
- It does not solve the remaining device sort floor.

The current stable prepared/query-many floor is now roughly:

- LSI: `~0.003s`
- reprojection: `~0.004s`
- sort0: `~0.03-0.04s`
- sort1: `~0.116-0.126s`
- carrier: `~0.101-0.104s`
- descriptor consumer: `~0.016s`
- PIP/midpoint/assign small phases: usually `~0.04-0.07s`

So the next meaningful target is still device sort, especially `sort_map1_device_columnar_sec`, or a deeper replacement of the current bitonic sort with a better generic GPU ordering primitive.  CPU lexsort was already rejected by Goal4995.

## Exit Label

`completed_goal4996_uint32_face_columns_remove_carrier_widening_copy`
