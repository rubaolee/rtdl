# Goal1267 v1.2 Targeted OptiX Pod Packet

Date: 2026-05-05

Valid: `True`
Source commit: `4d1cbc7fd16859d07c83728705713bd53d106df3`
Plan source: `docs/reports/goal1266_v1_2_optix_plan_after_v1_1_findings_2026-05-05.md`

## Archive

- path: `/Users/rl2025/rtdl_python_only/docs/reports/goal1267_rtdl_source_2026-05-05.tar.gz`
- sha256: `9e3c1f045d3eb9709ad9030893cfd38b5659105f6d244ad5f46a68c404a550f1`
- bytes: `1559079`

## Targets

| Priority | Row | Scales | Required evidence |
| --- | --- | --- | --- |
| 1 | `graph_analytics` | 30000, 60000 | `ray_pack_mode`, `blocker_pack_mode`, `blocker_pack_sec`, `ray_pack_sec`, `scene_prepare_sec`, `ray_prepare_sec`, `query_anyhit_count_sec`, `query_anyhit_count_first_sec`, `query_anyhit_count_mean_sec`, `query_anyhit_count_min_sec`, `visibility_query_repeats`, `summary_postprocess_sec` |
| 2 | `polygon_pair_overlap_area_rows` | 40000, 80000, 160000 | `candidate_count_matches_expected`, `candidate_count_delta_vs_expected`, `positive_pair_count_matches_expected`, `expected_positive_pair_count`, `optix_positive_pair_count`, `candidate_discovery_seconds`, `native_exact_continuation_seconds`, `output_seconds` |
| 3 | `database_analytics` | 100000, 300000 | `warm_query_median_seconds`, `prepare_seconds`, `one_shot_seconds`, `row_materializing_operation_count` |
| 4 | `polygon_set_jaccard` | 4096, 8192 | `chunk_copies`, `candidate_discovery_seconds`, `native_exact_continuation_seconds`, `output_seconds` |

## Preconditions

- Run only after local inspection says pod timing is needed.
- Use one RTX-class Linux pod session and reuse it for all four target rows.
- Collect same-contract Embree and OptiX artifacts before interpretation.
- Run the graph prepared-repeat probe from Goal1269 to separate repeated query cost from one-time scene/ray preparation.
- Preserve Goal1270 candidate diagnostics for polygon-pair and Jaccard artifacts.
- Do not open Vulkan, HIPRT, or Apple RT implementation work before v2.1.
- Copy back result tgz and sha256 before any intake report.

## Upload

```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/docs/reports/goal1267_rtdl_source_2026-05-05.tar.gz root@<pod_host>:/tmp/goal1267_rtdl_source_2026-05-05.tar.gz
```
```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/scripts/goal1267_v1_2_optix_targeted_pod_executor.sh root@<pod_host>:/tmp/goal1267_executor.sh
```

## Run On Pod

```bash
ARCHIVE=/tmp/goal1267_rtdl_source_2026-05-05.tar.gz EXPECTED_SHA256=9e3c1f045d3eb9709ad9030893cfd38b5659105f6d244ad5f46a68c404a550f1 WORKDIR=/workspace/rtdl_goal1267 RESULT_TGZ=/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz RESULT_SHA=/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz.sha256 bash /tmp/goal1267_executor.sh
```

## Copy Back

```bash
mkdir -p docs/reports/goal1267_live_pod_2026-05-05
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz docs/reports/goal1267_live_pod_2026-05-05/
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1267_v1_2_optix_targeted_pod_results.tgz.sha256 docs/reports/goal1267_live_pod_2026-05-05/
```
```bash
tar -xzf docs/reports/goal1267_live_pod_2026-05-05/goal1267_v1_2_optix_targeted_pod_results.tgz -C docs/reports/goal1267_live_pod_2026-05-05
```

## Boundary

This packet is execution-only v1.2 evidence collection. It does not authorize public wording, release claims, or positive speedup claims. Slower OptiX results may close only as optix_still_slower_with_reason when correctness and bottleneck evidence are preserved.
