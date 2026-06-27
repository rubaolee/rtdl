# Goal 402 Review: v0.6 RT Graph Final Correctness And Performance Closure

Date: 2026-04-14
Reviewer: Codex

## Verdict

ACCEPTED

## Review basis

This closure is accepted on a three-agent evidence chain:

1. Mac Codex direct audit and sync integration
2. Windows Codex benchmark/bug-fix handoff
3. Gemini review chain for:
   - Goal 400 correctness gate
   - Goal 401 performance gate

## Findings

### 1. The RT graph path is now demonstrated, not hypothetical

The repo now contains a coherent RT graph path spanning:

- DSL/kernel shape
- Python truth path
- native/oracle truth path
- Embree / OptiX / Vulkan backend mappings
- PostgreSQL correctness baseline

The final imported report and benchmark handoff consistently describe graph work
as lowered through RT-style traversal/intersection kernels rather than through a
separate conventional graph library path.

### 2. The earlier large-batch Embree triangle gap is materially resolved

The imported Windows delta provides a concrete and technically coherent fix:

- separate endpoint mark buffers in the Embree triangle probe path

The updated local test file now includes the previously missing asymmetric-degree
regression shape, and the focused Embree triangle test band is green locally.

### 3. The performance claims are strong enough, but should remain bounded

The imported final report provides real public-dataset anchors on:

- `wiki-Talk`
- `soc-LiveJournal1`
- `com-Orkut`

and shows a stable pattern:

- OptiX and Vulkan are the strongest RTDL graph backends
- Embree is slower but functional
- PostgreSQL remains valuable as an external baseline, not as the main
  performance target

That is enough to support the bounded statement that RTDL graph is
performance-credible.

## Remaining honesty boundary

The accepted version-level claim is:

- RTDL graph is real, correct on the validated slices, and performance-credible

The unaccepted stronger claim remains:

- RTDL graph is generally faster than specialized graph systems

## Acceptance statement

Goal 402 is accepted as the final bounded closure package for the corrected RT
`v0.6` graph line.
