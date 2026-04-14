# Goal 350 Report: v0.6 BFS Oracle Implementation

Date: 2026-04-13

## Summary

This slice adds the first compiled RTDL CPU/native implementation for the
opening `v0.6` BFS contract:

- CSR single-source BFS

## What was added

- native/oracle CSR BFS ABI and implementation
- Python runtime wrapper for native BFS rows
- public export surface
- focused parity tests against the Python BFS truth path

## Current boundary

This is the first compiled CPU/native graph baseline:

- not a generic graph DSL claim
- not an accelerated backend claim
- not a performance claim
