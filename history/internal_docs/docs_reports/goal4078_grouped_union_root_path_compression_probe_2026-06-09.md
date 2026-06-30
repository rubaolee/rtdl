# Goal4078 Grouped-Union Root Path Compression Probe

Date: 2026-06-09

## Status

Completed as a native OptiX probe and reverted after pod timing showed no material win.

## Purpose

Goal4074 showed that RT-DBSCAN's recommended route is dominated by the native fixed-radius grouped-union continuation. Goal4078 tests a generic union-find improvement inside that native continuation: opportunistic monotonic path compression while reading parent roots.

This is not DBSCAN-specific. It applies to the generic prepared fixed-radius grouped-union primitive used by RT-DBSCAN's recommended route.

## Probe Change

The OptiX grouped-union device root lookup now performs path halving:

- read `next = parent[root]`;
- read `grand = parent[next]`;
- if `grand < next`, apply `atomicMin(parent + root, grand)`;
- continue walking toward the root.

The update was monotonic because the grouped-union parent policy already uses smaller component roots as canonical representatives. The runtime metadata recorded:

`grouped_union_root_path_compression_policy = monotonic_atomic_min_path_halving_default`

## Pod Evidence

Artifacts:

- `docs/reports/goal4078_grouped_union_root_path_compression_probe_pod.json`
- `docs/reports/goal4078_grouped_union_root_path_compression_probe_pod.stdout.txt`
- `docs/reports/goal4078_grouped_union_root_path_compression_probe_summary.json`

Comparison against the post-reset-fusion Goal4075 baseline:

| Profile | baseline elapsed sec | probe elapsed sec | probe/baseline | baseline native sec | probe native sec | native ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d_65536` | 0.093612 | 0.093291 | 0.997x | 0.087976 | 0.088019 | 1.000x |
| `road3d_65536` | 0.035123 | 0.035556 | 1.012x | 0.029681 | 0.029819 | 1.005x |

The probe was correctness-stable by normalized component-size signatures, but it did not produce a meaningful native improvement. The extra atomics are therefore not justified as a default primitive behavior.

Decision: `revert_probe_no_material_win`.

## Acceptance Rule

The code path was reverted. The artifacts remain as negative/neutral evidence for future grouped-union design.

## Boundary

This does not add native ABI, app-specific engine logic, automatic dispatch, public speedup wording, release authorization, broad RT-core claims, whole-app claims, or true-zero-copy claims.
