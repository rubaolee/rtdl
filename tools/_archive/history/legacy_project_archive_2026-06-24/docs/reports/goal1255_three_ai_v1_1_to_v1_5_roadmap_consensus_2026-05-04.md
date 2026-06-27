# Goal1255 Three-AI Roadmap Consensus: v1.1 through v1.5

Date: 2026-05-04

Status: `ACCEPT`

## Scope

This consensus covers the post-v1.0 roadmap from v1.1 through v1.5 and the
pre-v2.1 backend scope rule.

## Inputs

- Codex roadmap:
  `docs/reports/goal1255_codex_v1_1_to_v1_5_roadmap_and_scope_2026-05-04.md`
- Gemini review:
  `docs/reports/goal1255_gemini_external_review_v1_1_to_v1_5_roadmap_2026-05-04.md`
- Claude review:
  `docs/reports/goal1255_claude_external_review_v1_1_to_v1_5_roadmap_2026-05-04.md`

## Consensus Verdict

`ACCEPT`

All three AIs accept the roadmap with no required fixes.

## Consensus Decisions

The accepted roadmap is:

- v1.1: post-release hardening and Embree/OptiX performance triage;
- v1.2: NVIDIA OptiX performance push against same-contract Embree baselines;
- v1.3: primitive ABI contract, per-app lowering matrix, backend parity
  contract, public wording contract, and migration gates;
- v1.4: compatibility-wrapper first migration slice;
- v1.5: reviewed generic traversal-plus-reduction primitive release.

The accepted backend scope is:

- before v2.1, do not spend new implementation effort on Vulkan, HIPRT, or
  Apple RT;
- preserve existing proof surfaces for those backends in documentation and
  tests;
- active implementation and performance work should focus on Embree and OptiX;
- NVIDIA OptiX/RTX performance is the top priority;
- Embree remains the CPU RT fallback and same-contract comparison baseline.

The accepted v1.5 primitive target remains the Goal1042/Goal1227 set:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN|MAX|SUM)`
- `REDUCE_INT(COUNT|SUM)`
- `COLLECT_K_BOUNDED` experimental only after scalar primitives are stable

## External Review Summary

Gemini accepted the roadmap and specifically agreed that:

- the v1.1-v1.4 ladder is technically sound;
- freezing Vulkan, HIPRT, and Apple RT before v2.1 is justified;
- OptiX/RTX should be the top performance lane while Embree remains the
  same-contract comparison baseline;
- the v1.5 primitive target matches Goal1042 and Goal1227;
- the roadmap does not overclaim public speedup or whole-app acceleration.

Claude accepted the roadmap and independently confirmed that:

- the ladder matches Goal1042's instruction to avoid broad backend rewrites;
- the pre-v2.1 freeze is a justified focus mechanism;
- v1.2 correctly forces OptiX performance evidence before v1.3/v1.4
  architectural migration;
- the four v1.1 triage targets are the right blocked/not-reviewed rows from
  the v1.0 inventory;
- Embree must remain baseline and fallback at every gate.

Claude noted one non-blocking documentation improvement: Goal1227 named a
public wording contract as a distinct pre-implementation artifact. The roadmap
now names that contract explicitly in v1.3.

## Boundary

This consensus authorizes beginning v1.1 planning and execution. It does not
authorize v1.5 native refactoring before the v1.3 contracts exist and are
externally reviewed.

This consensus does not authorize any new public speedup wording. Public
wording still requires reviewed exact-sub-path evidence and a separate wording
review packet.

This consensus does not reopen Vulkan, HIPRT, or Apple RT implementation work.
Those backends stay frozen for new implementation work until v2.1 or later,
unless a new externally reviewed decision supersedes this scope rule.
