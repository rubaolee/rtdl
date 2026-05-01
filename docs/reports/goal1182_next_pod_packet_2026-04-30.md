# Goal1182 Next Consolidated RTX Pod Packet

Date: 2026-04-30

Valid: `True`

## Archive

- path: `/Users/rl2025/rtdl_python_only/docs/reports/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz`
- sha256: `b5f7c732d927acaaf5daf1ee2840aef6943ab6e01e81138111df73f98fbd5e00`
- bytes: `1464522`
- manifest file count: `1726`
- manifest aggregate sha256: `e674619fcd7fff0b9802ba9f7b7ba2fe9113c30a848f3477c33270c26f77e544`

## Pod Batch

- base manifest: `scripts/goal1170_clean_source_rtx_batch_manifest.py`
- pod executor: `scripts/goal1176_pod_archive_batch_executor.sh`
- expected rows: `8`

## Preconditions

- Use an RTX-class Linux pod with NVIDIA driver visible through nvidia-smi.
- Do not patch source on the pod; the executor creates a synthetic clean git commit from this archive.
- Executor installs GEOS/pkg-config and CUDA dev packages before strict correctness gates.
- Run the full batch once per pod session and copy back the result archive plus SHA file.

## Upload

```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/docs/reports/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz root@<pod_host>:/tmp/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz
```
```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/scripts/goal1176_pod_archive_batch_executor.sh root@<pod_host>:/tmp/goal1182_executor.sh
```

## Run On Pod

```bash
ARCHIVE=/tmp/goal1182_rtdl_current_source_for_next_pod_2026-04-30.tar.gz EXPECTED_SHA256=b5f7c732d927acaaf5daf1ee2840aef6943ab6e01e81138111df73f98fbd5e00 WORKDIR=/workspace/rtdl_goal1182 RESULT_TGZ=/tmp/goal1182_goal1170_results.tgz RESULT_SHA=/tmp/goal1182_goal1170_results.tgz.sha256 bash /tmp/goal1182_executor.sh
```

## Copy Back

```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1182_goal1170_results.tgz docs/reports/goal1182_live_pod_2026-04-30/
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1182_goal1170_results.tgz.sha256 docs/reports/goal1182_live_pod_2026-04-30/
```

## Boundary

This packet prepares the next consolidated pod run. It creates a source archive and replay commands only; it does not run cloud benchmarks, authorize release, or authorize public RTX speedup wording.
