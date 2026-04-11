# Codex Consensus: Goal 215 v0.4 GPU Re-work Proposal

Date: 2026-04-10
Status: draft pending external review

## Verdict

This proposal is the correct correction to the earlier `v0.4` closure bar.

## Findings

- The earlier `v0.4` line was coherent under a CPU/oracle-plus-Embree
  interpretation, but that interpretation was too weak for RTDL's stated GPU
  RT-core purpose.
- Requiring OptiX closure for both new workloads is the right top-priority
  correction.
- Requiring Vulkan to run correctly, while not yet demanding optimized Vulkan
  performance, is the right secondary boundary.
- The proposal keeps the reopened line reviewable by separating OptiX and
  Vulkan work into distinct goals instead of hiding them under a vague
  "backend completion" label.

## Summary

Goal 215 should become the new `v0.4` working definition if at least one
external AI review agrees that the release bar must include GPU support for the
new nearest-neighbor workloads.
