# Goal969 RunPod RTX A5000 Execution Report

Date: 2026-04-26

## Scope

This report records the paid RTX pod execution requested after the final local
pre-pod readiness check.

Local source commit at copy time:

```text
7f569829fbad00f9bfa58e758b0fc4ee0324b410
```

Remote pod:

```text
host: 11e03eee29bc
gpu: NVIDIA RTX A5000
driver: 570.211.01
cuda toolkit used by build: /usr/local/cuda-12.4
python: 3.11.10
repo copy: /workspace/rtdl_python_only
```

The repo was copied without `.git`, so remote `git rev-parse` probes report
`not a git repository`. The commit above is the local source commit used for
the copy.

## Bootstrap

Initial bootstrap failed because the pod did not include OptiX headers:

```text
missing OptiX SDK header optix.h
```

NVIDIA `optix-dev` headers were installed from NVIDIA's public header
repository:

```bash
git clone --depth 1 --branch v8.0.0 https://github.com/NVIDIA/optix-dev /workspace/vendor/optix-dev-8.0.0
```

OptiX `v9.1.0` headers were also tried first, but the runtime rejected them:

```text
OptiX error: Unsupported ABI version
```

Using `v8.0.0` headers, bootstrap passed:

```text
make build-optix: ok
native OptiX focused tests: 30 tests OK
status: ok
```

Bootstrap artifacts:

```text
docs/reports/cloud_2026_04_26/runpod_a5000_0900/goal763_rtx_cloud_bootstrap_check.json
docs/reports/cloud_2026_04_26/runpod_a5000_0900/goal763_rtx_cloud_bootstrap_check_ok.json
```

## Group Results

| Group | Workloads | Status | Notes |
| --- | --- | --- | --- |
| A | robot_collision_screening / prepared_pose_flags | ok | Large compact timing run plus validated smaller companion. |
| B | outlier_detection, dbscan_clustering / fixed-radius summaries | ok | Large timing run plus validated smaller companion. |
| C | database_analytics / sales_risk, regional_dashboard | ok | Strict compact-summary DB runs with native phase counters. |
| D | service coverage, event hotspot, facility coverage threshold | ok | Facility threshold artifact is timing-oriented; boundary retained. |
| E | road hazard, segment/polygon hitcount, bounded pair rows | ok | Strict gates passed. |
| F | graph visibility/BFS/triangle gate | ok after remedy | First run failed due missing GEOS; passed after `libgeos-dev pkg-config`. |
| G | Hausdorff threshold, ANN candidate coverage, Barnes-Hut node coverage | ok | Prepared decision artifacts generated. |
| H | polygon overlap, polygon Jaccard | ok | Native-assisted phase gates passed. |

## Preserved Failure And Remedy

Group F first failed with:

```text
RTDL native oracle build failed ... cannot find -lgeos_c
```

Remedy applied on the same pod:

```bash
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y libgeos-dev pkg-config
```

Rerunning only Group F then passed strict mode.

Failure artifacts are intentionally preserved:

```text
docs/reports/cloud_2026_04_26/runpod_a5000_0900/goal761_group_f_graph_summary_failed.json
docs/reports/cloud_2026_04_26/runpod_a5000_0900/goal889_graph_visibility_optix_gate_rtx_failed.json
```

## Copied Artifacts

All copied artifacts are under:

```text
docs/reports/cloud_2026_04_26/runpod_a5000_0900/
```

Key summaries:

```text
goal761_group_a_robot_summary.json
goal761_group_b_fixed_radius_summary.json
goal761_group_c_database_summary.json
goal761_group_d_spatial_summary.json
goal761_group_e_segment_polygon_summary.json
goal761_group_f_graph_summary.json
goal761_group_g_prepared_decision_summary.json
goal761_group_h_polygon_summary.json
```

Validated companion artifacts:

```text
goal969_robot_pose_flags_validated_companion_rtx.json
goal969_fixed_radius_validated_companion_rtx.json
```

## Boundary

This run collects RTX execution evidence only.

It does not by itself authorize:

- public speedup claims
- v1.0 release
- whole-app acceleration claims where the artifact explicitly scopes to a
  prepared sub-path, compact summary, candidate discovery, or native-assisted
  phase

Those claims require local artifact review, updated documentation, and required
2-AI consensus.

## Current Verdict

The pod execution objective was completed: bootstrap plus Groups A-H all have
successful copied artifacts, with the Group F dependency failure documented and
remedied.
