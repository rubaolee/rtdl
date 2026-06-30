# Goal4384 V3.0 Preflight 3-AI Consensus Gate

Date: 2026-06-14

Status: gate definition and reviewer packet. This document does not authorize V3.0 implementation.

## Decision

V3.0 must not start until the project has an explicit 3-AI consensus over the V3.0 scope, architecture boundary, risks, and first milestone plan.

The required reviewers are:

| Reviewer role | Required artifact | Acceptable verdicts |
| --- | --- | --- |
| Codex primary proposal and self-audit | this report plus a final consensus document | `accept-with-boundary` only after external review is complete |
| Claude independent review | `docs/reviews/goal4384_claude_review_v3_0_preflight_2026-06-14.md` | `accept` or `accept-with-boundary` |
| Gemini independent review | `docs/reviews/goal4384_gemini_review_v3_0_preflight_2026-06-14.md` | `accept` or `accept-with-boundary` |

Any `needs-more-evidence`, `required-changes`, or `reject` verdict blocks V3.0 start until the evidence is repaired and reviewed again.

After independent Claude and Gemini review, this gate is strengthened with six binding conditions:

1. v2.14 closeout is a hard precondition for V3.0 implementation.
2. M1 must produce a frozen execution-graph IR design document before M2 code starts.
3. App-specific names are forbidden in the public Python API surface, not only in native C++/CUDA/OptiX symbols.
4. The RTDBSCAN pilot must prove at least one fused continuation primitive is reusable by another workload class.
5. Same-stream partner claims require hardware-observable evidence, such as CUDA events or Nsight stream correlation, before public wording.
6. No V3.0 public performance claim is authorized until the M5 release-grade benchmark harness is complete and externally reviewed.

These conditions are part of the gate, not optional reviewer suggestions.

## Hard Preconditions Before V3.0 Implementation

V3.0 implementation remains blocked until all of the following are true:

- the v2.14 release packet is complete;
- promoted v2.14 rows are GREEN/GREEN/YELLOW or better in the cross-app audit, or removed from public wording;
- RED-dimension rows are marked internal/review-only;
- v2.13 governance is explicit: either internal bridge or superseded-by-v2.14, without moving any published tag;
- the final Goal4384 consensus document records Codex, Claude, and Gemini acceptable verdicts;
- the strengthened boundary conditions in this document are tested and referenced by the final consensus.

## What Counts As Starting V3.0

The following are not allowed before consensus:

- creating or promoting a V3.0 architecture branch as implementation work;
- adding native V3.0 fused execution graph code;
- adding app-specific native engine semantics under the V3.0 name;
- changing public docs to claim V3.0 direction is accepted;
- starting benchmark-app rewrites that depend on unreviewed V3.0 planner assumptions.

The following are allowed before consensus:

- preparing review packets;
- finalizing v2.14 internal cleanup reports and gates;
- collecting missing evidence requested by reviewers;
- writing non-implementation design notes clearly marked as preflight.

## Why V3.0 Needs Consensus

V2.X has reached its natural boundary. It proved the RTDL design can express serious RT workloads through app-agnostic primitives, run both OptiX RT-core and Embree CPU backends, and support Python plus explicit partners for app-owned continuation. It also exposed that several remaining benchmark-app gaps are structural rather than local optimizations:

- RayJoin PIP/overlay need fused point-location, face-id, topology, and output assembly paths.
- RTDBSCAN is limited by device-side component continuation and convergence.
- Barnes-Hut needs opening traversal and force/vector accumulation fused as a generic aggregate-tree execution path.
- Contact and robot workloads need broadphase, refinement, compact flags, and app-owned output logic composed without repeated host materialization.
- Partner state, CUDA graph replay, same-stream continuation, and prepared query/state residency must become system-level concepts rather than one-off app scripts.
- Paper-scale benchmark harnessing must become a first-class discipline.

These are V3.0-class problems. Pushing them into V2.X would risk app-specific patches and blurry claim boundaries.

## Proposed V3.0 Architecture Boundary

V3.0 should preserve the existing RTDL rule:

> The native engine exposes app-agnostic primitives and execution contracts. Application semantics stay in Python or explicit partner continuation code.

V3.0 should add a generic execution layer around that rule:

1. **Primitive graph planner**: lowers app-declared primitive graphs into backend-specific prepared execution plans.
2. **Device-resident streams**: treats candidate rows, ids, flags, counts, summaries, and reductions as first-class values with explicit residency and lifetime.
3. **Fused generic continuations**: supports compact positives, grouped reductions, first/nearest/threshold summaries, component-style unions, frontier traversal, and vector sums without app-specific native vocabulary.
4. **Partner runtime protocol**: makes CuPy, Numba, Triton, and Torch continuations explicit, same-stream when possible, and measurable as part of the plan.
5. **Backend lowering**: supports OptiX RT cores, Embree CPU, CUDA partner kernels, and future HIPRT/AMD paths under one semantic contract.
6. **Profiler-grade phase accounting**: separates build, upload, traversal, kernel continuation, reduction, download, host wrapper, and presentation.
7. **Policy selection**: can honestly choose RT traversal, CUDA-core partner, Embree CPU, or hybrid paths depending on the workload rather than assuming RT cores always win.

## Non-Goals For V3.0

- No native RayJoin engine.
- No native DBSCAN engine.
- No native Barnes-Hut force-law engine.
- No native contact-manifold physics engine.
- No app-specific public Python API names for V3.0 planners, wrappers, factories, or plan builders.
- No automatic public speedup claims.
- No true-zero-copy claim unless pointer/lifetime/stream evidence proves it.
- No claim that RT cores always beat Embree or CUDA-core partners.
- No paper-reproduction claim without exact datasets and author-code timing basis.

## Proposed First Milestones

| Milestone | Purpose | Exit condition |
| --- | --- | --- |
| M0: consensus and scope freeze | Prevent V3.0 from becoming a vague rewrite | Codex, Claude, and Gemini all accept the scope and non-goals |
| M1: execution graph IR | Define app-agnostic graph values, residency, streams, and phase accounting | Frozen IR design document plus static tests validate graph contracts, residency annotations, phase markers, and no app-specific vocabulary |
| M2: RTDBSCAN fused continuation pilot | Turn fixed-radius core flags plus component continuation into a generic graph plan | Same-contract OptiX/Embree/CUDA-partner table with phase accounting, plus at least one non-DBSCAN workload reusing the fused continuation primitive without modification |
| M3: RayJoin PIP/overlay pilot | Add generic face-id/point-location/compact topology streams without RayJoin-native ABI | Compare author code, RTDL OptiX, and RTDL Embree under separated timing bases |
| M4: aggregate-tree pilot | Generalize Barnes-Hut node coverage into frontier/vector-sum execution | Traversal and vector continuation measured separately and together |
| M5: release-grade benchmark harness | Make paper datasets, author code, pod runs, and phase tables repeatable | Public packet has exact artifacts, scripts, CUDA-event/Nsight-grade evidence for same-stream claims, and multi-AI review |

## Public Claim Rule

No V3.0 public performance claim is authorized by this preflight gate. A public V3.0 claim requires M5 completion, exact artifacts, row-scoped wording, named hardware, named backend, named partner when used, phase explanation, and a fresh Claude/Gemini review over the exact claim packet.

## Review Questions

1. Is V2.X correctly treated as complete enough to freeze after v2.14 cleanup rather than continuing indefinite optimization inside V2.X?
2. Does the proposed V3.0 architecture preserve the app-agnostic native engine rule?
3. Are the non-goals strong enough to prevent app-specific native rewrites?
4. Are RTDBSCAN and RayJoin the right first V3.0 pilots, or should the first pilot be a smaller generic graph primitive?
5. Does the partner runtime plan correctly treat CuPy/Numba/Triton/Torch as explicit user/app continuations rather than hidden RTDL magic?
6. What evidence must exist before V3.0 implementation begins?
7. What evidence must exist before any V3.0 public performance claim?

## Current Consensus Status

| Reviewer | Status | Notes |
| --- | --- | --- |
| Codex | proposed, not final | Codex recommends V3.0 only after this 3-AI gate passes. |
| Claude | pending | Review packet prepared; no callable Claude connector is available in this session. |
| Gemini | pending | Review packet prepared; no callable Gemini connector is available in this session. |
| Final consensus | blocked | Must wait for Claude and Gemini reviews. |

## Binding Rule

Until the final consensus document records three acceptable verdicts, V3.0 is `blocked_preflight`. The project may continue v2.14 cleanup and evidence gathering, but V3.0 implementation must not begin.
