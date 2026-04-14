# v0.6 Goal Sequence

Date: 2026-04-13

This is the initial bounded goal ladder for `v0.6` after the `v0.5.0` release.

## Version theme

`v0.6` should extend RTDL from geometry and nearest-neighbor workloads into
graph applications motivated by the SIGMETRICS 2025 ray-tracing-core graph
case-study line.

## Entry workloads

- `bfs`
- `triangle_count`

## Expected opening sequence

Goal 337:

- version plan and scope boundary for graph workloads

Goal 338:

- graph workload charter and semantic contract

Goal 339:

- graph data / layout contract

Goal 340:

- BFS truth path

Goal 341:

- triangle-count truth path

Goal 342:

- first backend closure for BFS

Goal 343:

- first backend closure for triangle count

Goal 344:

- bounded Linux graph evaluation and paper-correlation report

Goal 345:

- BFS truth-path implementation

Goal 346:

- triangle-count truth-path implementation

Goal 347:

- PostgreSQL graph-baseline plan

Goal 348:

- PostgreSQL BFS baseline implementation

Goal 349:

- PostgreSQL triangle-count baseline implementation

Goal 350:

- BFS compiled CPU/native implementation

Goal 351:

- triangle-count compiled CPU/native implementation

Goal 352:

- bounded graph evaluation harness

Goal 353:

- code review and test gate

Goal 354:

- Linux live PostgreSQL graph baseline

Goal 355:

- bounded Linux graph evaluation

Goal 356:

- real graph dataset preparation

Goal 357:

- wiki-Talk BFS bounded evaluation

Goal 358:

- real-data bounded BFS evaluation summary

Goal 359:

- wiki-Talk triangle-count bounded evaluation

Goal 360:

- real-data bounded triangle-count evaluation summary

Goal 361:

- audit adoption and evaluation correction

Goal 362:

- larger bounded Linux real-data graph evaluation

Goal 363:

- next real-data scale plan

Goal 364:

- split-bound next-scale Linux graph evaluation

Goal 365:

- split-bound scale-plus-one Linux graph evaluation

Goal 366:

- second real dataset plan

Goal 367:

- bounded `cit-Patents` dataset preparation

Goal 368:

- first bounded `cit-Patents` BFS evaluation

Goal 369:

- first bounded Linux `cit-Patents` BFS evaluation

Goal 370:

- DuckDB out-of-scope baseline decision

Goal 371:

- bounded `cit-Patents` triangle-count plan

Goal 372:

- bounded `cit-Patents` triangle-count probe

Goal 373:

- bounded Linux `cit-Patents` triangle-count probe

Goal 374:

- `cit-Patents` split-bound scale plan

Goal 375:

- `cit-Patents` split-bound Linux evaluation

Goal 376:

- `v0.6` release surface cleanup

Goal 377:

- total code review and test gate before release

Goal 378:

- total doc review, update, and verification before release

Goal 379:

- total goal-flow audit before release

Goal 380:

- final external release review

Goal 381:

- final release decision

Goal 382:

- release-make state

## Boundaries

- Linux remains the first performance platform
- Windows and macOS should begin as correctness platforms unless evidence
  justifies more
- `v0.6` starts from bounded graph applications, not a claim of a general graph
  DSL or full paper reproduction
