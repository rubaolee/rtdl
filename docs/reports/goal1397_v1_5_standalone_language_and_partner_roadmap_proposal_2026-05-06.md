# Goal 1397 - v1.5 Standalone Language And Partner Roadmap Proposal

Date: 2026-05-06

## Status

This document proposes a roadmap boundary change requested by the project owner.
It supersedes the earlier narrow interpretation of v1.5 as only a reviewed
generic scalar primitive release.

This proposal does not create a release, tag, public speedup claim, or partner
API. It changes the intended milestone semantics if accepted by 3-AI consensus.

## Proposed Roadmap Change

Previous boundary:

- v1.5: reviewed generic traversal-plus-reduction primitive release.
- v1.6-v1.9: bounded collection, app migration, per-app benchmarks, and public
  support maturity.
- v2.0: broader runtime/performance architecture.

New boundary:

- v1.5: complete RTDL as an independent Embree+OptiX language/runtime without a
  partner mechanism.
- v1.6-v2.0: build the new partner mechanism step by step.

The reason for the change is product coherence. A public v1.5 release should
not stop at a primitive packet if the intended claim is that RTDL is an
independent language. Under the new boundary, v1.5 must finish the standalone
language contract first; partner interfaces start only after that line is
closed.

## v1.5 Completion Definition

RTDL v1.5 is complete only when RTDL can be described as a standalone
Embree+OptiX language/runtime with honest, tested boundaries.

Required v1.5 work:

- Stabilize `COLLECT_K_BOUNDED` or explicitly exclude row-returning apps from
  standalone-complete scope.
- Define stable semantics for row collection if promoted: `K`, overflow,
  truncation, ordering, per-query capacity, memory limits, and CPU/Embree/OptiX
  parity behavior.
- Migrate selected app endpoints from app-name-specific native shortcuts toward
  generic language primitives or compatibility wrappers over those primitives.
- Produce an app migration matrix that says which apps are fully generic,
  wrapper-backed, scalar-only, collection-dependent, frozen, or demo-only.
- Run same-contract per-app Embree/OptiX benchmark suites for the v1.5 app
  surface, separating prepare, query, reduction, copy-back, Python continuation,
  validation, and total wall time.
- Promote public performance wording only for exact subpaths that have fresh
  evidence and required review.
- Publish a v1.5 support/maturity matrix backed by tests.
- Preserve source-tree usage wording unless packaging metadata is added:
  `PYTHONPATH=src:. python ...`.
- Keep Vulkan, HIPRT, and Apple RT frozen before v2.1 except for preserving
  existing proof surfaces.

Non-goals for v1.5:

- no partner mechanism;
- no new Vulkan/HIPRT/Apple RT implementation push;
- no universal compute engine claim;
- no broad whole-app speedup claim without separately reviewed evidence;
- no package-install claim without packaging work.

## v1.6-v2.0 Partner Mechanism Track

After standalone RTDL v1.5 is complete, v1.6-v2.0 should build partner support
incrementally.

| Version | Partner-track goal | Required outcome |
| --- | --- | --- |
| v1.6 | Partner API design | Define what a partner backend, compute engine, app adapter, or data bridge may implement; define capability reporting and fallback rules. |
| v1.7 | First partner prototype | Integrate one external-style partner through the new interface without weakening the standalone Embree+OptiX path. |
| v1.8 | Partner conformance suite | Add correctness, capability, fallback, error-isolation, and benchmark-reporting tests for partner implementations. |
| v1.9 | Partner ecosystem hardening | Provide templates, docs, versioning policy, compatibility policy, failure isolation, and review gates. |
| v2.0 | Public partner-ready RTDL | Ship a stable partner extension API/ABI or Python-facing plugin contract with conformance gates and release-quality onboarding docs. |

The v2.0 target becomes partner-ready RTDL, not "rewrite RTDL as a general
native compute compiler." RTDL should remain an RT-centered language/runtime
with explicit interfaces to partners for non-RT phases.

## Consequences For Current Release Readiness

Under this proposal, Goal1395's "ready for explicit v1.5 release operation"
conclusion is no longer sufficient for the new v1.5 scope. It remains valid as
evidence that the stable scalar primitive packet is ready, but not as evidence
that standalone-language v1.5 is complete.

Therefore:

- do not tag `v1.5` from the current primitive-only state;
- keep the Goal1393 primitive evidence as a prerequisite artifact;
- keep Goal1394 public wording consensus as valid only for the primitive packet;
- require new v1.5 completion gates before release/tag;
- update project memory so future work does not regress to the old v1.5 scope.

## Proposed Next Execution Order

1. Record this roadmap change with 3-AI consensus.
2. Update project-level memory and release-readiness notes to mark v1.5 as
   standalone-language completion, not primitive-only release.
3. Define the v1.5 standalone completion gate file.
4. Implement or explicitly defer `COLLECT_K_BOUNDED`.
5. Migrate app endpoints and classify app maturity.
6. Run per-app Embree/OptiX benchmark and correctness suites.
7. Prepare the actual v1.5 release only after the standalone gates pass.

## Codex Position

Codex accepts the roadmap change as technically coherent if the release gate is
updated immediately. The main risk is scope expansion: v1.5 becomes materially
larger and should not be tagged until the collection, app migration, and per-app
benchmark gates are complete.

