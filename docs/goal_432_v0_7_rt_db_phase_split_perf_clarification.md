# Goal 432: v0.7 RT DB Phase-Split Performance Clarification

## Goal

Measure the first bounded `v0.7` DB workload family with an explicit RTDL
phase split so RTDL and PostgreSQL can both be read as two-phase systems on
Linux.

## Required outcome

- explicit RTDL `prepare` and `execute` timing for:
  - `embree`
  - `optix`
  - `vulkan`
- PostgreSQL `setup` and `query` retained in the same artifact
- honest interpretation of:
  - RTDL total vs PostgreSQL total
  - RTDL execute vs PostgreSQL query

## Review requirement

This goal requires at least 2-AI consensus before closure.
