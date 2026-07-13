# Goal4968 Planar-Map LSI Workspace Preparation Contract

Date: 2026-07-04

## Exit Label

`completed_generic_planar_map_lsi_workspace_contract__prepared_hot_boundary_explicit`

## Purpose

Goal4967 showed that the large fresh LSI cost is mostly first-use workspace and
cache preparation, while the prepared-hot pair-id operation is tiny.

Goal4968 turns that observation into a generic RTDL contract:

> A planar-map LSI base/query pair can explicitly prepare its reusable
> workspace before hot pair-id/count execution.

This is not a RayJoin overlay feature. RayJoin is only the measurement app.

## Implementation

### Runtime API

File:

```text
src/rtdsl/optix_runtime.py
```

New public method:

```python
PreparedOptixPlanarMapLsi2DQuery.prepare_workspace() -> dict[str, object]
```

Contract:

- builds the reusable planar-map LSI workspace for the already prepared base
  and query segment sets,
- returns metadata and native timings,
- preserves the generic `PLANAR_MAP_LSI_2D` primitive boundary,
- does not expose application workflow semantics,
- does not import or call bundled RayJoin helpers.

Metadata schema:

```text
rtdl.optix.planar_map_lsi_2d.prepared_workspace.v1
```

Key claim-boundary fields:

```json
{
  "public_generic_rtdl_primitive": true,
  "bundled_rayjoin_helper_used": false,
  "workspace_depends_on_base_and_query": true,
  "full_application_supported": false,
  "rayjoin_specific_core_primitive": false,
  "broad_speedup_claim_authorized": false
}
```

### RayJoin Paper-Reproduction App

File:

```text
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
```

The prepared-hot route now calls:

```python
query.prepare_workspace()
```

and records:

```text
lsi_prepare_workspace_sec
lsi_prepared_replay_rows_sec
native_lsi_timings["prepared_workspace"]
native_lsi_timings["prepared_replay_pair_id_rows"]
```

This replaces the older implicit warmup that ran pair-id rows once as a side
effect.

## Local Structural Tests

Command:

```bash
py -m unittest \
  tests.goal4968_planar_map_lsi_workspace_contract_test \
  tests.goal4964_exact_lsi_pair_id_device_columns_test \
  tests.goal4955_projected_descriptor_pipeline_test \
  tests.goal4956_columnar_xsect_pipeline_test \
  tests.goal4947_lsi_pair_columns_numba_handoff_test
```

Result:

```text
Ran 16 tests
OK (skipped=2)
```

The new test verifies that the workspace contract is generic and that the
public app uses `query.prepare_workspace()` rather than a hidden pair-row
warmup.

## POD Measurement

POD:

```text
root@213.173.108.15 -p 10689
workspace: /root/rtdl_goal4955
```

Input:

```text
left:  br_county_clean_25_odyssey_final.txt
right: br_soil_ascii_odyssey_final.txt
author_overlay_compute_sec: 0.0421
```

Command shape:

```bash
python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left ...br_county_clean_25_odyssey_final.txt \
  --right ...br_soil_ascii_odyssey_final.txt \
  --pair-name br_county_soil \
  --device-columnar \
  --compiled-group \
  --prepared-lsi-replay \
  --author-overlay-compute-sec 0.0421 \
  --summary /tmp/goal4968_prepared_workspace_runN.json
```

Artifacts:

```text
history/internal_docs/goal4955_artifacts/goal4968_prepared_workspace_run1.json
history/internal_docs/goal4955_artifacts/goal4968_prepared_workspace_run2.json
history/internal_docs/goal4955_artifacts/goal4968_prepared_workspace_run3.json
```

## Results

Semantic fingerprint was stable in all runs:

```text
lsi_row_count = 20860
pair_count = 28815
total_groups = 64459
total_point_rows = 673371
```

Median timings:

| Phase | Median |
|---|---:|
| `prepare_lsi_session_sec` | `0.276912s` |
| `lsi_prepare_workspace_sec` | `0.533379s` |
| `lsi_prepared_replay_rows_sec` | `0.001456s` |
| `writer_free_hot_sec` | `0.091702s` |
| ratio vs AuthorPatch `0.0421s` | `2.18x` |

Run 1 had a known warm-start outlier in non-LSI downstream work:

```text
writer_free_hot_sec = 0.707669s
```

Runs 2 and 3 were stable:

```text
0.091341s
0.091702s
```

## Interpretation

### I1. The prepared workspace contract is real and generic

The new public method belongs to the generic planar-map LSI primitive:

```text
PLANAR_MAP_LSI_2D
```

It exposes workspace preparation for a base/query pair. It does not expose
RayJoin output chains, overlay text, faces, or app-specific semantics.

### I2. The measured boundary is now explicit

There are two honest costs:

| Boundary | Cost |
|---|---:|
| one-shot fresh, including session/workspace first use | about `0.90s` from prior fresh measurements |
| prepared-hot workspace replay | about `0.092s` steady state |

Allowed claim:

```text
With an already prepared planar-map LSI workspace, the writer-free binary route
runs at about 0.092s on the public sample.
```

Forbidden claim:

```text
One-shot fresh overlay is 0.092s.
```

### I3. The next bottleneck moved

After explicit workspace preparation:

```text
hot pair-id rows ~= 0.0015s
writer_free_hot ~= 0.092s
```

The remaining prepared-hot route is no longer dominated by LSI. It is dominated
by downstream numeric app work:

- reprojection,
- sort,
- point-location,
- midpoint construction,
- group construction/consumer.

That means the next optimization depends on the product target:

- If the target is one-shot script latency: reduce `prepare_lsi_session_sec`
  and `lsi_prepare_workspace_sec`.
- If the target is database/dataflow steady-state throughput: optimize the
  remaining prepared-hot downstream phases and use the prepared boundary as the
  normal operator contract.

## Revised Next Goals

### Goal4969: Prepared-Hot Downstream Phase Breakdown

Purpose:

- measure which non-LSI phase dominates the `~0.092s` steady-state route,
- avoid chasing LSI after it is already small in prepared-hot mode.

### Goal4970: Workspace Preparation Cost Reduction

Purpose:

- if one-shot latency matters, break down and reduce:
  - base prepare,
  - query prepare,
  - scaled LSI cache build,
  - grouped-range build.

### Goal4971: Larger Representative Prepared-Workspace Test

Purpose:

- restore a larger representative dataset,
- test whether the prepared/fresh split holds beyond the public sample.

## Not Authorized

- No claim that one-shot fresh overlay is `0.092s`.
- No claim that RTDL is broadly faster than AuthorPatch.
- No RayJoin-specific core primitive.
- No claim that larger representative data has been tested.
- No claim that the app text writer route is solved.
