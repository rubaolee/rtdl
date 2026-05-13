# Goal1814: v2.0 Strict Birth Gate

Status: `needs-more-evidence`

Date: 2026-05-13

## Decision

The v2.0 label is stricter than the earlier bounded partner-candidate gate.
The current Python+partner evidence is valuable and should remain in the
history, but it is a preview path, not the birth of v2.0.

v2.0 is born only when RTDL can honestly present Python+partner+RTDL as a
finished public release surface, not merely a host-staged first bridge.

## Supersedes

This gate supersedes the release-readiness conclusion in:

- `docs/reports/goal1810_v2_0_release_readiness_audit_2026-05-13.md`
- `docs/reviews/goal1813_3ai_consensus_v2_0_release_readiness_2026-05-13.md`

Those files remain valid evidence for the first partner any-hit preview, but
they no longer authorize a v2.0 release label.

## Required Before v2.0

The following blockers must be solved, or explicitly removed from the v2.0
public scope by a new 3-AI consensus, before v2.0 can be released:

| Blocker | Required outcome |
| --- | --- |
| True zero-copy | Measured partner-owned memory path with artifacts proving no hidden host copy for the claimed path. |
| Direct device-pointer handoff | Public descriptor path that hands CUDA device pointers or DLPack-equivalent device memory into the backend with stream/lifetime rules. |
| Broad RT-core speedup | Reviewed performance evidence for exact RT-core-backed paths on RTX-class hardware, with phase timings and same-contract baselines. |
| Whole-application acceleration | App-level benchmark evidence for each app claim, not only primitive microbenchmarks. |
| Arbitrary PyTorch/CuPy acceleration boundary | Clear user-facing positive and negative rule for what RTDL can and cannot accelerate inside partner programs; no implication that arbitrary framework code is optimized. |
| Package-install support | Validated packaging metadata and install commands, or a 3-AI-ratified release statement that v2.0 remains source-tree-only and does not claim package-install support. |

## Current Accepted Evidence

The current evidence accepted for the preview path is:

- protocol-first partner contract;
- PyTorch as the reference partner;
- CuPy as the conformance partner;
- NumPy as the CPU/Embree partner path;
- public partner any-hit dispatch for Embree and OptiX;
- RTX-class OptiX pod execution for the tiny any-hit fixture;
- explicit `transfer_mode = "host_stage"`;
- explicit `true_zero_copy_authorized = false`;
- explicit `rt_core_speedup_claim_authorized = false`.

This is enough to keep developing the v2.0 partner track, but it is not enough
to call v2.0 released.

## Current Public Wording

Allowed wording before v2.0:

```text
RTDL includes an experimental Python+partner preview path: partner-owned NumPy,
PyTorch CUDA, and CuPy CUDA columns can be passed through a host-staged public
Python API to the RTDL any-hit primitive path for Embree and OptiX.
```

Blocked wording before v2.0:

- `RTDL v2.0 is released.`
- `RTDL has general true zero-copy support.`
- `RTDL hands partner device pointers directly to the backend.`
- `RTDL broadly accelerates partner programs on RT cores.`
- `RTDL accelerates whole applications by default.`
- `RTDL accelerates arbitrary PyTorch/CuPy code.`
- `RTDL supports package installation.`

## Work Plan To Reach v2.0

1. Finish a real device-memory descriptor path with lifetime and stream rules.
2. Extend the partial Goal1823 device-ray path into a measured zero-copy or
   direct device-pointer evidence packet on an RTX pod for one narrow OptiX
   primitive.
3. Expand from aggregate any-hit to the minimum app-unlocking partner primitive
   set, starting with row output or grouped summaries for any-hit/count-hit.
4. Rewrite selected learner apps through those partner primitives only where the
   public partner surface actually supports the app contract.
5. Produce same-contract whole-app evidence for the rewritten apps.
6. Add package metadata or keep v2.0 explicitly source-tree-only by consensus.
7. Refresh user docs, release reports, and the public claim gate.
8. Obtain new 3-AI consensus after the evidence exists.

## Review Notes

Goal1815 is preserved as a non-substantive first Gemini response because it did
not perform the requested technical audit. Goal1816 provides a substantive
Claude review and Goal1817 provides a substantive Gemini follow-up review.

The substantive external review boundary is now incorporated into this gate:

- the arbitrary PyTorch/CuPy blocker requires a positive rule for what RTDL does
  accelerate, not only a negative list of blocked claims;
- any source-tree-only v2.0 release decision must be ratified by 3-AI
  consensus, not by Codex alone.

## Verdict

`needs-more-evidence`: the partner track is real, but v2.0 is not born yet.
