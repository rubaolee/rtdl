# Codex Consensus: Goal 577 v0.9.0 Release Action

Date: 2026-04-18

Verdict: ACCEPT.

The v0.9.0 release action is justified after Goal575 and Goal576. The live
public docs and `VERSION` were converted from candidate wording to released
v0.9.0 wording, while historical pre-release reports were preserved as evidence
artifacts. Local full test discovery passes 239 tests, focused public-doc audit
passes with no stale release-candidate wording or missing links, and
`git diff --check` passes.

The release boundary remains honest: HIPRT is released for the accepted Linux
HIPRT/Orochi CUDA-mode matrix, not AMD-GPU validated and not a CPU fallback;
closest-hit is released on CPU reference, `run_cpu`, and Embree only.
