# Goal 367: v0.6 bounded cit-Patents dataset preparation

## Why this goal exists

Goal 366 selected `graphalytics_cit_patents` as the second real dataset for the
bounded `v0.6` graph line.

Before any BFS evaluation on that dataset, the repo needs an honest preparation
slice that makes the raw edge-list acquisition path explicit and testable.

## Scope

In scope:

- strengthen graph dataset metadata so `cit-Patents` has an explicit raw
  download path
- add a bounded fetch helper for the raw `cit-Patents` archive
- extend focused dataset-prep tests so the new dataset path is covered

Out of scope:

- downloading the large dataset inside the repo
- running the first `cit-Patents` BFS evaluation
- any new backend or runtime work

## Exit condition

This goal is complete when the repo has:

- saved bounded `cit-Patents` dataset-prep docs
- focused tests covering the metadata/fetch path
- a saved external review
- a saved Codex consensus note
