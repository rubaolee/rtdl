# Goal3826 Scale-Profile Calibration On A5000

Date: 2026-06-07

Status: evidence recorded; follow-up engineering required.

## Purpose

Goal3823 and Goal3825 prove the current ten benchmark front doors execute and
keep their claim boundaries. Goal3826 asks a different question: which larger
profiles are reasonable candidates for future performance packets?

This is not a release packet and not a public speedup claim. It is calibration
for later scale-profile registries.

## Artifacts

- `docs/reports/goal3826_scale_profile_candidate_a5000/summary.json`
- `docs/reports/goal3826_scale_profile_calibration_a5000/summary.json`
- `docs/reports/goal3826_barnes_hut_calibration_a5000/summary.json`

All runs used the A5000 pod at commit `b00286c5`.

## First Candidate Sweep

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `hausdorff_xhd_scale` | pass | 1.752 | safe but still too short for a long timing profile |
| `spatial_rayjoin_pip_count_repeat` | pass | 1.752 | safe but still too short for a long timing profile |
| `rt_dbscan_numba_65536` | timeout | 241.517 | too heavy for a bounded scale profile |
| `robot_collision_4096` | timeout | 240.336 | too heavy for a bounded scale profile |
| `contact_manifold_grid64` | pass | 0.751 | safe but too short |
| `raydb_style_count_262k` | pass | 2.252 | safe medium profile candidate |
| `barnes_hut_numba_8192` | timeout | 300.350 | too heavy; exposes Barnes-Hut Numba scalability cliff |
| `librts_spatial_index_32768` | pass | 2.003 | safe medium profile candidate |
| `rtnn_prepared_optix_65536` | pass | 3.003 | safe medium profile candidate |
| `triangle_counting_native_2048` | pass | 1.752 | safe but still short |

## Calibration Follow-Up

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `rt_dbscan_numba_8192` | pass | 8.005 | good scale-profile candidate |
| `rt_dbscan_numba_16384` | pass | 23.262 | usable stress candidate |
| `rt_dbscan_numba_32768` | pass | 88.544 | heavy stress candidate, not default |
| `robot_collision_1024` | pass | 11.532 | good scale-profile candidate |
| `robot_collision_2048` | timeout | 180.394 | too heavy for default scale profile |
| `barnes_hut_numba_2048` | timeout | 180.316 | too heavy; confirms Barnes-Hut Numba cliff |
| `barnes_hut_numba_4096` | timeout | 240.322 | too heavy |

## Barnes-Hut Ladder

| Candidate | Status | Elapsed seconds | Reading |
| --- | --- | ---: | --- |
| `barnes_hut_numba_1152` | timeout | 90.323 | cliff appears immediately above the 1024 smoke row |
| `barnes_hut_numba_1280` | timeout | 120.356 | still timed out |
| `barnes_hut_numba_1536` | timeout | 150.371 | still timed out |

## Interpretation

Seven of the first ten larger candidates passed quickly, but the naive 65k
RT-DBSCAN, 4096-pose robot, and 8192-body Barnes-Hut choices were too heavy.
Calibration then found usable RT-DBSCAN and robot scale points:

- RT-DBSCAN: `8192` points is a good default scale profile; `16384` is a
  heavier stress row; `32768` is too long for default smoke but useful for
  deep performance work.
- Robot collision: `1024` poses with 128 obstacles is a good scale profile;
  `2048` poses times out under the current command.
- Barnes-Hut: the current no-RawKernel Numba exact-force path has a severe scaling cliff above 1024 bodies. This is now a P0 follow-up for the partner
  reference lane, not a documentation problem.

## Next Engineering Target

Do not promote a Barnes-Hut scale profile until the Numba exact-force path is
fixed or replaced by a better generic partner continuation. The likely focus is
the `pairwise_inverse_square_force_2d_partner_columns` Numba block-reduction
path or the surrounding app materialization path.

## Boundary

Goal3826 does not authorize release action, package-install wording, public
speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, AMD performance wording,
automatic partner selection, or app-specific native-engine logic.

It is a calibration packet for future scale-profile work.
