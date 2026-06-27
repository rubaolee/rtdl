# Goal 19 Spec

## Title

RTDL vs Pure C/C++ Embree Performance Comparison

## Motivation

Goal 17 and Goal 18 established that RTDL can materially reduce host-path overhead while preserving the Python-like DSL. The remaining question is whether the latest RTDL runtime paths are close enough to pure native Embree to satisfy the project's performance bar.

## Goal

Measure and compare:

- RTDL dict path
- RTDL first-class raw path
- RTDL prepared raw path
- pure native C/C++ + Embree path

on matched workloads and matched inputs.

## Minimum Scope

- `lsi`
- `pip`

## Runtime Budget

The default local comparison package should finish in roughly `5–10 minutes` total on this Mac.

`lsi` and `pip` may use different larger-profile sizes in order to stay inside that total runtime window.

## Desired Extension

If practical, add native comparison paths for more current workloads. But no acceptance claim depends on workloads without real native baselines.

## Acceptance Bar

1. correctness parity is established before timing claims
2. fixture-scale and larger-profile comparisons are separated clearly
3. default local run stays within the intended `5–10 minute` window
4. report states the gap between latest RTDL paths and pure native Embree
5. report states clearly whether the current architecture is sufficient or needs another redesign slice
