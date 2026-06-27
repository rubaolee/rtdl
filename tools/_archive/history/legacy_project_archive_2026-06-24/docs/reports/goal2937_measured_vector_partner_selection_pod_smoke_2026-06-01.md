# Goal2937: Measured Vector Partner Selection Pod Smoke

Date: 2026-06-01
Status: pod smoke passed

## Purpose

Goal2937 validates the Goal2936 measured partner-selection helper on the RTX
pod with real Torch, Triton, and CuPy CUDA execution.

Artifact:

`docs/reports/goal2937_measured_partner_selection_pod/goal2937_measured_partner_selection.json`

## Pod Evidence

- source commit: `9f477c02e97a676b4d7a79056039df2877e6e5c8`
- source dirty: `[]`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- groups: `8192`
- rows per group: `16`
- selected partner: `cupy`

| Partner | Status | Median seconds |
| --- | --- | ---: |
| Torch | `pass` | `0.001388422` |
| Triton | `pass` | `0.004785148` |
| CuPy | `pass` | `0.000703857` |

The selected partner was CuPy because it won the caller-requested same-contract measurement.
This is expected for this dense presegmented
grouped vector-sum shape and matches the Goal2933/Goal2934 Barnes-Hut lesson.

## Result

The helper is now more than a mocked local API: it has live pod evidence across
the three currently supported CUDA partner families for this continuation. This
supports the v2.5 user story that a Python program can explicitly compare
partner continuations and choose the best one while RTDL keeps the native RT
engine app-agnostic.

## Boundary

This is not a v2.5 release authorization, public speedup claim, broad RT-core
claim, whole-app speedup claim, true-zero-copy claim, automatic partner selection claim,
package-install claim, paper-reproduction claim, or
app-specific native engine logic claim.

The helper measures partner continuations only; it does not execute RT
traversal and does not make CuPy, Torch, or Triton globally preferred.
