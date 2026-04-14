# Goal 367 Report: v0.6 bounded cit-Patents dataset preparation

Date: 2026-04-13

## Summary

This slice prepares the second real dataset selected in Goal 366:
- `graphalytics_cit_patents`

The goal stays bounded to preparation. It does not claim evaluation closure.

## What was added

- graph dataset metadata now carries an explicit `download_url`
- `graphalytics_cit_patents` is mapped to the raw SNAP archive:
  - `https://snap.stanford.edu/data/cit-Patents.txt.gz`
- a bounded fetch helper script was added:
  - `scripts/goal367_fetch_cit_patents.py`
- focused tests now verify:
  - `graphalytics_cit_patents` remains in the candidate set
  - metadata lookup resolves the expected download URL

## Why this is the right next move

- Goal 366 already chose `cit-Patents` as the next real dataset
- the repo previously had only `wiki-Talk`-oriented fetch support
- this closes the preparation gap without pretending the first
  `cit-Patents` workload run already exists

## Current boundary

This is still a bounded prep slice:

- not a live `cit-Patents` evaluation
- not a full dataset ingestion pipeline
- not a benchmark claim
- not a paper-scale reproduction claim
