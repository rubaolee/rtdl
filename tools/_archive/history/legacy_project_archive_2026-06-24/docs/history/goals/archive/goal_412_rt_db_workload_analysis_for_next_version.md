# Goal 412: RT Database Workload Analysis For The Next Version

## Goal

Analyze the RT database-workload direction from:

- `/Users/rl2025/Downloads/2024-rtscan.pdf`
- `/Users/rl2025/Downloads/2025-raydb.pdf`

and determine what kind of database-style operations RTDL should support in
the next version without claiming to become a full database system.

## Scope boundary

- this is a workload/surface analysis goal, not an implementation goal
- the output must identify RT-friendly database workload families
- the output must identify explicit non-goals
- the output must stay aligned with RTDL as a bounded RT-kernel/runtime system,
  not a SQL database engine

## Required outcome

- a report that explains what RTScan contributes
- a report that explains what RayDB contributes
- a synthesis of the common RT-friendly database pattern
- a proposed RTDL workload scope for the next version
- explicit rejected scope, so the next version is not mis-scoped
- a short staged roadmap for how such support should be introduced in RTDL

## Minimum conclusions the report must address

- whether RTDL should target OLTP or OLAP-style work
- whether joins should be in or out of the first database-style RTDL version
- whether grouped aggregation is in scope
- whether denormalized / wide-table assumptions should be explicit
- whether preprocessing / offline build assumptions should be explicit
- whether RTDL should present a DBMS surface or a bounded workload-kernel surface

## Review requirement

This goal requires 3-AI consensus before closure:

- Gemini
- Claude
- Codex
