# Goal 39 OptiX Backend Audit

Date: 2026-04-02

## What Was Audited

Two external artifacts were provided:

- Gemini review:
  [Iteration_0_Original_Review_2026-04-02_Gemini.md](/Users/rl2025/rtdl_python_only/history/revisions/2026-04-02-goal-39-optix-backend-audit/external_reports/Iteration_0_Original_Review_2026-04-02_Gemini.md)
- Claude implementation log:
  [Iteration_0_Implementation_Log_2026-04-02_Claude.txt](/Users/rl2025/rtdl_python_only/history/revisions/2026-04-02-goal-39-optix-backend-audit/external_reports/Iteration_0_Implementation_Log_2026-04-02_Claude.txt)

The claimed implementation was reviewed in Claude's workspace:

- `/Users/rl2025/claude-work/2026-04-02/rtdl`

The controlled RTDL repository was also checked:

- `/Users/rl2025/rtdl_python_only`

## Main Audit Result

The OptiX backend is **not currently present in the controlled RTDL repository**.

The main repository still contains:

- OptiX code generation skeletons
- OptiX-oriented lowering metadata
- documentation that says the real OptiX runtime is still future work

It does **not** contain:

- `src/native/rtdl_optix.cpp`
- `src/rtdsl/optix_runtime.py`
- a merged runnable OptiX execution backend

So the current project status remains:

- OptiX runtime implementation is external and unmerged
- Embree remains the only controlled execution backend

## Concrete Findings Against Claude's Implementation

### 1. Payload-register count mismatch in multiple pipelines

Claude's OptiX implementation creates some pipelines with too few payload registers relative to the `optixTrace(...)` calls used by the kernels.

Affected areas include:

- PIP
- ray-hitcount
- segment-polygon-hitcount

This is a real OptiX correctness/integration problem and blocks treating the implementation as ready.

### 2. Overlay containment fallback is weaker than claimed

The implementation comments and Gemini review describe a hybrid overlay strategy that checks containment after edge intersections. But the current CPU-side supplement only checks the first vertex from each polygon pair, not a full or clearly sufficient containment condition.

So the overlay path is not yet trustworthy as a complete correctness-preserving implementation.

### 3. Default build/load path is inconsistent on macOS

Claude's `Makefile` writes:

- `build/librtdl_optix.so`

but the Python loader searches for:

- `build/librtdl_optix.dylib` on Darwin

This means the advertised default build/load path is broken on macOS unless the caller manually overrides the library path.

## Review of Gemini's Review Quality

Gemini's original review was useful in one narrow sense:

- it identified the intended architecture and major claimed components
- it correctly treated the implementation as a Linux/NVIDIA-oriented backend
- it did not overclaim local macOS execution success

But the review quality is not sufficient for acceptance.

### Strengths

- good high-level summary of the claimed design
- recognized that execution was not actually run on local NVIDIA hardware
- called out documentation and capacity issues as future hardening items

### Weaknesses

- it accepted the implementation as near-complete without catching the payload-register mismatch
- it described the overlay strategy as correct without checking whether the containment supplement was actually complete
- it did not notice that the implementation was not merged into the controlled RTDL repository
- it treated API parity and import success as stronger evidence than they really are

### Overall Judgment

Gemini's review quality was:

- useful for initial orientation
- not reliable enough for merge or acceptance

So a second Gemini review is required, but it must be guided by the concrete findings above instead of reusing the earlier optimistic frame.

## Corrected Project Status

After this audit, the correct OptiX status is:

- external prototype exists in Claude's workspace
- code has real implementation work, not just a stub
- code is not accepted
- code is not merged
- code still has blocking issues
- RTDL still does not have a controlled runnable OptiX backend

## Required Next Review Loop

The next OptiX round should proceed in this order:

1. Gemini re-reviews the audit findings and acknowledges the earlier review overreached.
2. Claude revises the external OptiX implementation only in:
   - `/Users/rl2025/claude-work/2026-04-02/rtdl`
3. Codex reviews the revised implementation file-by-file.
4. Gemini reviews the revised implementation and Codex review.
5. Final consensus is recorded only after the revision is re-audited.
6. Only then may the accepted OptiX changes be copied into the controlled RTDL repository.

## Recommended Revision Targets for Claude

Claude's next OptiX revision must at minimum fix:

1. payload-register count mismatches across pipelines
2. overlay containment correctness gap
3. build/load artifact naming inconsistency
4. any additional integration issues discovered during Codex re-review

## Conclusion

The correct conclusion is not that RTDL now has a completed OptiX backend.

The correct conclusion is:

- a substantial external OptiX prototype exists,
- Gemini's first review overstated its readiness,
- and the project now has a concrete audited basis for a corrected OptiX revision round under an external-workspace-first rule.
