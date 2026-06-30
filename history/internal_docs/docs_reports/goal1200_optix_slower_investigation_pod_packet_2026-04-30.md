# Goal1200 OptiX Slower-App Investigation Pod Packet

Date: 2026-04-30

Valid: `True`

## Archive

- path: `/Users/rl2025/rtdl_python_only/docs/reports/goal1200_rtdl_source_2026-04-30.tar.gz`
- sha256: `4f77dbde17c8baefab4c79130f446ceb4b2d7d72279b9755f7605dedd4ebaa66`
- bytes: `1502233`

## Pod Batch

- reviewed_plan: `docs/reports/goal1197_optix_slower_app_investigation_manifest_2026-04-30.md`
- post_same_scale_sync: `docs/reports/goal1199_two_ai_consensus_2026-04-30.md`
- pod_executor: `scripts/goal1200_optix_slower_investigation_pod_executor.sh`
- remote_result: `/tmp/goal1200_optix_slower_app_investigation.tgz`
- local_copyback_dir: `docs/reports/goal1200_live_pod_2026-04-30`

## Preconditions

- Use one RTX-class Linux pod session; do not restart per app.
- Use the local key that exists on this Mac, usually ~/.ssh/id_ed25519_rtdl_codex.
- Executor preserves failed status JSON and logs instead of aborting the whole batch.
- Copy the result tgz and sha256 back before interpretation.
- A separate intake/review goal must interpret results after copy-back.

## Upload

```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/docs/reports/goal1200_rtdl_source_2026-04-30.tar.gz root@<pod_host>:/tmp/goal1200_rtdl_source_2026-04-30.tar.gz
```
```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/scripts/goal1200_optix_slower_investigation_pod_executor.sh root@<pod_host>:/tmp/goal1200_executor.sh
```

## Run On Pod

```bash
ARCHIVE=/tmp/goal1200_rtdl_source_2026-04-30.tar.gz EXPECTED_SHA256=4f77dbde17c8baefab4c79130f446ceb4b2d7d72279b9755f7605dedd4ebaa66 WORKDIR=/workspace/rtdl_goal1200 RESULT_TGZ=/tmp/goal1200_optix_slower_app_investigation.tgz RESULT_SHA=/tmp/goal1200_optix_slower_app_investigation.tgz.sha256 bash /tmp/goal1200_executor.sh
```

## Copy Back

```bash
mkdir -p docs/reports/goal1200_live_pod_2026-04-30
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1200_optix_slower_app_investigation.tgz docs/reports/goal1200_live_pod_2026-04-30/
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1200_optix_slower_app_investigation.tgz.sha256 docs/reports/goal1200_live_pod_2026-04-30/
```
```bash
tar -xzf docs/reports/goal1200_live_pod_2026-04-30/goal1200_optix_slower_app_investigation.tgz -C docs/reports/goal1200_live_pod_2026-04-30
```

## Boundary

This packet prepares a future pod execution path for Goal1200 investigation evidence. It creates a source archive and replay commands only; it does not run cloud, edit public docs, authorize release, or authorize public RTX speedup wording.
