# Goal4215 Current Benchmark Scale-Profile Refresh After RT-DBSCAN Policy Canonicalization

Date: 2026-06-09

Status: internal evidence accepted with boundary

## Purpose

Goal4215 reruns the current ten benchmark-app scale-profile packet after the
Goal4205-4212 RT-DBSCAN boundary-policy cleanup. The specific check is that the
current benchmark front doors still execute on a real NVIDIA pod after
`single_pass_candidate_root_rebased` became the canonical/default RT-DBSCAN
boundary assignment policy.

This is an engineering health packet. It does not authorize release action,
public speedup wording, whole-app acceleration wording, broad RT-core wording,
paper-reproduction wording, true-zero-copy wording, automatic partner selection,
AMD performance wording, or app-specific native-engine logic.

## Hardware And Source

- Hardware: ephemeral RTX cloud validation pod; live SSH endpoint and local key
  names intentionally redacted from tracked evidence.
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.08`
- Source commit: `63289bbcd74326e0b44b865a3f66061cb49e823d`
- Runner: `scripts/goal3828_current_benchmark_scale_profile_runner.py`
- Packet: `docs/reports/goal4215_current_benchmark_scale_profile_after_policy_rtx4000ada/current_scale_profile_packet.json`

The first run produced a single environment failure: the RayJoin public-CDB
fixture directory was missing on the pod. The fixture was regenerated through
the existing `scripts/goal2159_rayjoin_public_cdb_runner.py` dry-run
materialization path, producing:

- `/root/rtdl/data/rayjoin_public_cdb/br_county_start256_count512.cdb`
- `/root/rtdl/data/rayjoin_public_cdb/br_soil_start256_count512.cdb`

The packet was then rerun coherently and passed all ten rows. The packet's
`runtime_environment.working_tree_clean` is `false` only because the runner
created the new `docs/reports/goal4215_...` artifact directory before recording
metadata; the source commit is fixed to `63289bbc`, and no source edits were
made on the pod.

## Packet Result

The final packet passed all ten promoted benchmark rows (`10/10`):

| App | Row | Status | Runner wall sec | Key timing signal |
| --- | --- | ---: | ---: | --- |
| Hausdorff/X-HD | `hausdorff_xhd_scale_default_optix_threshold` | pass | 1.502 | threshold-count query `0.007683s` |
| Spatial RayJoin | `spatial_rayjoin_public_cdb_representative_mixed_route_scale_default` | pass | 10.506 | PIP one-shot OptiX/Numba `0.249x`; repeated PIP batch `1.307x` per request; LSI `262.5x`; overlay `212.2x` |
| RT-DBSCAN | `rt_dbscan_optix_numba_scale_default_65536_no_validation` | pass | 3.503 | adapter median `0.097142s`; grouped native `0.091034s`; policy `single_pass_candidate_root_rebased` |
| Robot collision | `robot_collision_optix_scale_default_1024_no_probe_reference` | pass | 5.004 | traversal median `0.0000409s` over 49,900 measured runs |
| Contact manifold | `contact_manifold_optix_scale_default_grid64` | pass | 0.752 | native collect `0.000289s`; 64 valid candidates |
| RayDB-style | `raydb_style_optix_count_scale_default_262k` | pass | 6.504 | prepared primitive median `0.000893s`; traversal `0.000209s`; 262,144 rows |
| Barnes-Hut | `barnes_hut_numba_scale_default_8192` | pass | 1.502 | Numba force-kernel median `0.009040s`; no raw CUDA kernel required |
| LibRTS spatial index | `librts_spatial_index_optix_scale_default_32768` | pass | 2.002 | query median `0.044629s` |
| RTNN | `rtnn_prepared_optix_scale_default_65536` | pass | 3.253 | prepared ranked-summary median `0.000211s`; 206,256 bounded neighbors |
| Triangle counting | `triangle_counting_optix_rt_graph_2a1_scale_default_2048` | pass | 1.502 | query median `0.158139ms` |

## Interpretation

This packet is useful in three ways:

1. It confirms the current ten promoted benchmark front doors still run after
   the RT-DBSCAN policy cleanup.
2. It confirms the broad benchmark packet now observes the canonical
   `single_pass_candidate_root_rebased` RT-DBSCAN boundary policy, with
   `grouped_stream_continuation_pass_count = 1`.
3. It keeps the mixed-route story honest: RayJoin remains contract-split,
   RT-DBSCAN remains explicit user-selected OptiX+Numba, and primitive-first
   rows remain primitive-first.

The packet is not a final performance release table. It is a current-route
health and direction packet. It deliberately keeps release/public claim flags
false.

## Boundary

All release/public-claim flags in the packet remain false, and every parsed row
has an empty `claim_flag_violations` list. Any future release packet still needs
separate user authorization and the required multi-AI consensus process.
