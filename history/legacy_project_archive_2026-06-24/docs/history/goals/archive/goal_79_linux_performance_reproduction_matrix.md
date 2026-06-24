# Goal 79: Linux Performance Reproduction Matrix

Date: 2026-04-04
Status: complete

## Goal

Build a Linux-only performance reproduction matrix for the available RayJoin-style experiment surfaces, comparing:

- PostGIS
- RTDL Embree
- RTDL OptiX

The goal is to measure the available and finishable workload families honestly, ignoring unavailable or unstable dataset families instead of blocking on them.

## Scope

- Linux host only
- performance comparisons only
- backends:
  - PostGIS
  - Embree
  - OptiX
- dataset families that are available and runnable in the current project environment
- exact provenance for each included dataset and package

## Required Timing Boundary Rule

This goal must keep timing boundaries separate.

Accepted boundary labels:

- end-to-end
- prepared-execution or prepacked
- cached repeated-call

The final matrix and summary report must not merge those boundaries into a single performance table.

## Non-Goals

- no Python oracle performance evaluation
- no native C oracle performance evaluation
- no Vulkan performance evaluation
- no claims about unavailable or unstable dataset families
- no paper-identical reproduction claims for datasets that are not obtainable

## Required Outcome

Goal 79 is accepted if it produces:

- a Linux performance matrix covering all available and finishable RayJoin-style experiment surfaces
- exact dataset provenance and timing-boundary labels for every included row
- per-surface timing artifacts
- a final summary that states:
  - where PostGIS wins
  - where Embree wins
  - where OptiX wins
  - what was skipped because unavailable
- 2+ AI review before publication
