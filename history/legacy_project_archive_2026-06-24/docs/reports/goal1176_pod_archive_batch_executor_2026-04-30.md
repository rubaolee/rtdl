# Goal1176 Pod Archive Batch Executor

Date: 2026-04-30

## Purpose

Goal1176 provides the pod-side script for the reviewed staged-source archive
path. It is intended for a paid RTX pod window after uploading:

- `docs/reports/goal1175_rtdl_staged_source_2026-04-30.tar.gz`
- `scripts/goal1176_pod_archive_batch_executor.sh`

## Command

```bash
ARCHIVE=/tmp/goal1175_rtdl_staged_source_2026-04-30.tar.gz \
EXPECTED_SHA256=e6978ed37cdab26737df80efbcb1d34411900a66f9ce1c79063620d128bcce37 \
bash /tmp/goal1176_pod_archive_batch_executor.sh
```

## Behavior

- verifies archive SHA256 before extraction;
- extracts to `/workspace/rtdl_goal1176/rtdl_staged_source`;
- initializes a synthetic clean git repository for the extracted archive and
  exports `RTDL_SOURCE_COMMIT=goal1175-archive-<sha256>`;
- records environment and GPU data;
- regenerates the Goal1170 manifest/report files inside `docs/reports` because
  the staged archive excludes generated reports;
- installs Linux prerequisites including GEOS and CUDA NVRTC development package;
- installs OptiX headers under `/root/vendor/optix-dev`;
- builds `librtdl_optix.so`;
- runs the Goal1171 preflight through the Goal1170 runner;
- runs all eight Goal1170 batch rows;
- packages copied-back results to `/tmp/goal1176_goal1170_results.tgz`.

## Boundary

This script prepares and runs a pod batch. The resulting artifacts still require
local copyback, intake, external review, and public-wording review before any
claim-grade RTX wording is authorized.
