# Goal 356 Report: v0.6 Real Graph Dataset Preparation

Date: 2026-04-13

## Summary

This slice adds the first bounded real-graph dataset preparation support for
`v0.6`.

## What was added

- candidate real dataset metadata for:
  - SNAP `wiki-Talk`
  - Graphalytics `wiki-Talk`
  - Graphalytics `cit-Patents`
- bounded SNAP-style edge-list loader with:
  - plain-text support
  - `.gz` support
  - optional edge cap for bounded prep

## Why this is the right first real-data step

- `wiki-Talk` is a recognizable real graph family
- it fits BFS directly
- it gives `v0.6` a real-data path without pretending large-scale closure is
  already complete

## Current boundary

This is a bounded data-preparation slice:

- not a large benchmark closure
- not a final dataset policy for all future graph workloads
- not a graph-language change
