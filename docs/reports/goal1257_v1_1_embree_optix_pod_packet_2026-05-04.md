# Goal1257 v1.1 Embree/OptiX Pod Packet

Date: 2026-05-04

Valid: `True`
Source commit: `3e97eba6fcbf0abbb9ec286e264e486fcc6d648a`

## Archive

- path: `/Users/rl2025/rtdl_python_only/docs/reports/goal1257_rtdl_source_2026-05-04.tar.gz`
- sha256: `0c455b4190955292bf46cb9ed41e9600ed17132356bc5e7f7cb5e82046211048`
- bytes: `1542026`

## Pod Batch

- triage_report: `docs/reports/goal1256_v1_1_embree_optix_triage_2026-05-04.md`
- pod_executor: `scripts/goal1257_v1_1_embree_optix_pod_executor.sh`
- remote_result: `/tmp/goal1257_v1_1_embree_optix_pod_results.tgz`
- local_copyback_dir: `docs/reports/goal1257_live_pod_2026-05-04`

## Target Rows

- `database_analytics`
- `graph_analytics`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

## Preconditions

- Use one RTX-class Linux pod session and reuse it for all rows.
- Do not open Vulkan, HIPRT, or Apple RT implementation work.
- Copy back result tgz and sha256 before interpretation.
- Interpretation must be a separate intake/review step before any public wording.

## Upload

```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/docs/reports/goal1257_rtdl_source_2026-05-04.tar.gz root@<pod_host>:/tmp/goal1257_rtdl_source_2026-05-04.tar.gz
```
```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/scripts/goal1257_v1_1_embree_optix_pod_executor.sh root@<pod_host>:/tmp/goal1257_executor.sh
```

## Run On Pod

```bash
ARCHIVE=/tmp/goal1257_rtdl_source_2026-05-04.tar.gz EXPECTED_SHA256=0c455b4190955292bf46cb9ed41e9600ed17132356bc5e7f7cb5e82046211048 WORKDIR=/workspace/rtdl_goal1257 RESULT_TGZ=/tmp/goal1257_v1_1_embree_optix_pod_results.tgz RESULT_SHA=/tmp/goal1257_v1_1_embree_optix_pod_results.tgz.sha256 bash /tmp/goal1257_executor.sh
```

## Copy Back

```bash
mkdir -p docs/reports/goal1257_live_pod_2026-05-04
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1257_v1_1_embree_optix_pod_results.tgz docs/reports/goal1257_live_pod_2026-05-04/
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1257_v1_1_embree_optix_pod_results.tgz.sha256 docs/reports/goal1257_live_pod_2026-05-04/
```
```bash
tar -xzf docs/reports/goal1257_live_pod_2026-05-04/goal1257_v1_1_embree_optix_pod_results.tgz -C docs/reports/goal1257_live_pod_2026-05-04
```

## Boundary

This packet prepares current-source v1.1 Embree/OptiX timing collection. It does not run cloud, change public docs, authorize release, or authorize public RTX wording.
