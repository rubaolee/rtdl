# RTDL v0.8.0 Tag Record

Date: 2026-04-18
Status: authorized for release tag

## Current Decision

Tag `v0.8.0` is authorized for the Goal532 release commit.

The user explicitly authorized release on 2026-04-18 after the pre-release test,
documentation, and audit gates had passed. This document records the release
boundary that the tag must represent.

## What Is Ready

- six accepted v0.8 app-building examples
- public tutorials and example docs refreshed through Goal527
- capability boundaries refreshed for ANN/outlier/DBSCAN and app-building scope
- macOS post-doc-refresh audit accepted in Goal528
- Linux post-doc-refresh validation accepted in Goal529
- Claude/Gemini/Codex consensus records exist through Goal529
- complete history map remains valid through Goal529

## Required Before Tagging

Before tagging `v0.8.0`:

- complete external review of this v0.8 release package
- confirm no newer external tester reports have arrived unresolved
- confirm current worktree is clean
- confirm final release authorization is explicit

## Proposed Tag Boundary

`v0.8.0` should be described as:

- app-building release over the released `v0.7.0` surface
- six RTDL-plus-Python examples
- no new full DBMS/ANN/clustering/robotics/simulation/framework claim
- no general speedup claim
- Linux-primary validation with bounded macOS local validation

## Current Tag Status

The tag is authorized for creation from the Goal532 release commit after the
Goal532 review, tests, history registration, and commit complete.
