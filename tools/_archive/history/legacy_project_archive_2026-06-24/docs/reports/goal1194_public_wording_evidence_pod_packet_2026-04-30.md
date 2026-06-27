# Goal1194 Public Wording Evidence Pod Packet

Date: 2026-04-30

Valid: `True`

## Archive

- path: `/Users/rl2025/rtdl_python_only/docs/reports/goal1194_rtdl_source_2026-04-30.tar.gz`
- sha256: `a0d685b3b28a3045c187b720477f8a6ce1f3b5a3739e125ff33a20fb77082805`
- bytes: `1488357`
- manifest file count: `1759`
- manifest aggregate sha256: `67c4bab9c9207835de506122a400a50f61d94563e76951344d6afd80641e5ce2`

## Pod Batch

- runner: `scripts/goal1192_public_wording_evidence_batch_runner.sh`
- intake: `scripts/goal1193_public_wording_evidence_batch_intake.py`
- pod executor: `scripts/goal1194_public_wording_evidence_pod_executor.sh`
- expected artifacts: `12`
- expected app pairs: `6`

## Preconditions

- Use one RTX-class Linux pod session and run the full batch once.
- Use the local key that actually exists, usually ~/.ssh/id_ed25519_rtdl_codex on this Mac.
- Do not patch source on the pod; the executor creates a synthetic clean git commit from the archive.
- Executor installs GEOS/pkg-config before Embree/geometry baselines.
- Executor builds OptiX before running Goal1192.
- Copy the result tgz and sha256 back, then run Goal1193 intake locally before interpreting timing.

## Upload

```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/docs/reports/goal1194_rtdl_source_2026-04-30.tar.gz root@<pod_host>:/tmp/goal1194_rtdl_source_2026-04-30.tar.gz
```
```bash
scp -P <pod_port> -i <ssh_key> /Users/rl2025/rtdl_python_only/scripts/goal1194_public_wording_evidence_pod_executor.sh root@<pod_host>:/tmp/goal1194_executor.sh
```

## Run On Pod

```bash
ARCHIVE=/tmp/goal1194_rtdl_source_2026-04-30.tar.gz EXPECTED_SHA256=a0d685b3b28a3045c187b720477f8a6ce1f3b5a3739e125ff33a20fb77082805 WORKDIR=/workspace/rtdl_goal1194 RESULT_TGZ=/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz RESULT_SHA=/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz.sha256 bash /tmp/goal1194_executor.sh
```

## Copy Back And Intake

```bash
mkdir -p docs/reports/goal1194_live_pod_2026-04-30
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz docs/reports/goal1194_live_pod_2026-04-30/
```
```bash
scp -P <pod_port> -i <ssh_key> root@<pod_host>:/tmp/goal1194_goal1192_public_wording_evidence_batch.tgz.sha256 docs/reports/goal1194_live_pod_2026-04-30/
```
```bash
tar -xzf docs/reports/goal1194_live_pod_2026-04-30/goal1194_goal1192_public_wording_evidence_batch.tgz -C docs/reports/goal1194_live_pod_2026-04-30
```
```bash
PYTHONPATH=src:. python3 scripts/goal1193_public_wording_evidence_batch_intake.py --input-dir docs/reports/goal1194_live_pod_2026-04-30/docs/reports/goal1192_public_wording_evidence_batch --output-json docs/reports/goal1194_goal1192_public_wording_evidence_batch_intake_2026-04-30.json --output-md docs/reports/goal1194_goal1192_public_wording_evidence_batch_intake_2026-04-30.md
```

## Boundary

This packet prepares a future pod execution path for Goal1192 evidence. It creates a source archive and replay commands only; it does not run cloud, does not authorize release, and does not authorize public RTX speedup wording.
