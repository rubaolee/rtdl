# Goal1296 v1.5 Prepared Scene Session Pod Intake

Date: 2026-05-05

## Scope

This intake records real OptiX evidence for the Goal1295 reusable generic
prepared scene API. It is internal v1.5 evidence only.

## Pod

- SSH target: `root@213.173.99.11 -p 39006`
- Remote worktree: `/workspace/rtdl_goal1292`
- Source commit on pod: `b2506bdabf0eb5bfe8d84ee920899bd64b3d93b4`
- Local artifact:
  `docs/reports/goal1296_v1_5_prepared_scene_session_pod_results/session_evidence.json`

## Result

The runner prepared one OptiX scene and executed two ray batches against it:

- fixture: 256 copies, 512 rays, 256 triangles
- batch count: 2
- query repeats per batch: 100
- `scene_prepare_paid_once`: true
- `all_batches_match_cpu`: true
- scene prepare: `0.8000057451426983` sec

Batch A:

- rays: 256
- expected CPU hit count: 128
- OptiX hit count: 128
- first query: `0.00014013610780239105` sec
- mean query: `0.00007259244099259376` sec
- min query: `0.0000616610050201416` sec
- repeated query total: `0.0072592440992593765` sec
- ray prepare: `0.0006600804626941681` sec
- scene prepare charged this batch: `0.0` sec

Batch B:

- rays: 256
- expected CPU hit count: 128
- OptiX hit count: 128
- first query: `0.00006359070539474487` sec
- mean query: `0.00005480503663420677` sec
- min query: `0.00005292147397994995` sec
- repeated query total: `0.005480503663420677` sec
- ray prepare: `0.0002804994583129883` sec
- scene prepare charged this batch: `0.0` sec

## Interpretation

Goal1295 works on real OptiX: a single generic prepared scene can serve
multiple ray batches while preserving CPU hit-count parity. This confirms the
correct local direction after Goal1294: the optimization boundary is reusable
prepared state and host-side packing, not the any-hit query kernel.

## Boundary

No public speedup wording is authorized. No whole-app claim is authorized.
Vulkan, HIPRT, and Apple RT remain frozen for new implementation work before
v2.1.
