# Goal 241: System-Level Audit Database

Date: 2026-04-11
Status: implemented

## Objective

Build a durable file-level audit system for the full RTDL repository so that
every code and documentation file can be reviewed, tracked, and updated over
time instead of handled through scattered one-off reports.

## Audit Order

The database must preserve the user-priority audit order:

1. front page
2. tutorials
3. docs
4. examples
5. code-facing surface
6. tests / reports / history

## Requirements

The system must support per-file records for:

- path
- category / priority tier
- status
- correctness check state
- suggestions
- predictions

## Deliverables

- SQLite schema
- inventory builder script
- generated database
- generated summary report
