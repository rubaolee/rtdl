# Goal4498 / V3 M102 RTNN Paper Dataset Targets

## Conclusion

RTNN paper reproduction is not currently ready, and the reason is now precise: the paper input labels are known, but exact dataset recipes are not frozen in this repo or in the public author repository snapshot. Current uniform, shell, and clustered rows remain RTDL-internal distribution evidence only.

The target set is nine paper rows: four KITTI scale labels, three Stanford scan labels, and two Millennium/N-body labels. Bounded KITTI or sampled Stanford packages are allowed only as bounded reproduction artifacts with explicit labels; they must not be reported as paper rows.

## Target Matrix

| Target | Family | Points | Status | Priority |
|---|---|---:|---|---|
| `KITTI-1M` | `kitti_velodyne_point_sets` | 1,000,000 | `blocked_on_frame_recipe` | `phase_1` |
| `KITTI-6M` | `kitti_velodyne_point_sets` | 6,000,000 | `blocked_on_frame_recipe` | `phase_1` |
| `KITTI-12M` | `kitti_velodyne_point_sets` | 12,000,000 | `blocked_on_frame_recipe` | `phase_1` |
| `KITTI-25M` | `kitti_velodyne_point_sets` | 25,000,000 | `blocked_on_frame_recipe` | `phase_1` |
| `Bunny-360K` | `stanford_3d_scan_point_sets` | 360,000 | `blocked_on_scan_to_point_recipe` | `phase_2` |
| `Dragon-3.6M` | `stanford_3d_scan_point_sets` | 3,600,000 | `blocked_on_scan_to_point_recipe` | `phase_2` |
| `Buddha-4.6M` | `stanford_3d_scan_point_sets` | 4,600,000 | `blocked_on_scan_to_point_recipe` | `phase_2` |
| `NBody-9M` | `nbody_or_millennium_snapshots` | 9,000,000 | `blocked_on_snapshot_trace_recipe` | `phase_3` |
| `NBody-10M` | `nbody_or_millennium_snapshots` | 10,000,000 | `blocked_on_snapshot_trace_recipe` | `phase_3` |

## Acquisition Rule

- Phase 1: obtain or reconstruct an exact KITTI frame recipe for `KITTI-1M`, `KITTI-6M`, `KITTI-12M`, and `KITTI-25M` before any paper wording.
- Phase 2: freeze exact Stanford scan variants and point extraction/downsample rules for Bunny, Dragon, and Buddha.
- Phase 3: freeze Millennium trace/snapshot ids and coordinate extraction rules for the 9M and 10M rows.
- Author RTNN code can be used as the RT-core baseline, but its public repository snapshot only includes `src/samplepc.txt` as a sample input, not the paper datasets.

## Source Basis

- RTNN paper: https://horizon-lab.org/pubs/ppopp22.pdf
- Author repository: https://github.com/horizon-research/rtnn
- Author repo probe commit: `5532e7031d0c8268ffa555972f074f8882b379b5`

Artifacts:

- `docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.json`
- `docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.jsonl`
