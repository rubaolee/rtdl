# Gemini Review: Goal 78 — Vulkan Positive-Hit Sparse Redesign

**Reviewer:** Gemini CLI  
**Date:** 2026-04-04  
**Status:** Approved with minor risk observations

---

## 1. Executive Summary

The proposed redesign for Goal 78 successfully transitions the Vulkan `positive_only`
path from a legacy pure-CPU `O(P x Q)` scan to a modern two-stage GPU-accelerated sparse
pipeline.

## 2. Technical Evaluation

### Sparse Candidate Generation (Stage 1)

- Uses an atomic counter in `kPipPosRahit` to append `(point_index, poly_index)` pairs
  to a compact list.
- Eliminates the legacy host-side `O(P x Q)` nested exact-test scan.
- Replaces a pure CPU scan with a sparse GPU-to-host candidate transfer.

### Host Exact Finalization (Stage 2)

- Downloads only the valid candidate rows using a sub-copy pattern.
- Revalidates candidates on the host using GEOS or `exact_point_in_polygon(...)`.
- Preserves parity by keeping final truth on the host.

## 3. Risk Assessment

- **Low:** Params naming asymmetry across shaders is a maintenance risk.
- **Medium:** Candidate buffer is still worst-case preallocated.
- **Medium:** No physical Vulkan hardware validation yet.

## 4. Verdict

**Approved.**

Recommended next step:

- run the GPU smoke tests in `tests/rtdsl_vulkan_test.py`
- optionally unify the Params naming across the positive-hit shaders

## Note

This file is a repo-local copy of the external review originally produced at:

- `/Users/rl2025/gemini-work/Gemini_Goal78_Vulkan_Review_2026-04-04.md`
