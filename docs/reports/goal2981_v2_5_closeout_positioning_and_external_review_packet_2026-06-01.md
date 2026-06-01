# Goal2981 v2.5 Closeout Positioning And External Review Packet

Date: 2026-06-01

Status: v2.5 closeout packet ready for external review; no release authorization

## Purpose

Goal2981 closes the four-item v2.5 closeout sequence proposed by the Claude
roadmap:

| Roadmap item | Closure |
| --- | --- |
| C-1 primitive-first policy | Goal2978 encoded primitive-first native RTDL as the fast path, explicit partners for unfused continuations, and no auto-Triton rule. |
| C-2 representative same-contract gates | Goal2979 refreshed RayDB, RT-DBSCAN, and grouped-vector partner-choice evidence on RTX 4000 Ada at current main. |
| C-3 neutral-seam decision | Goal2980 explicitly scoped full partner-neutral composition out of v2.5. |
| C-4 honest closeout | This report records the delivered/not-delivered boundary and prepares external review. |

## v2.5 Position

The honest v2.5 statement is:

> RTDL v2.5 is an internal closeout candidate for a correct, app-agnostic,
> composable runtime whose fast path is primitive-first native RTDL, with
> explicit app/user-chosen partner continuations only when the continuation is
> not expressible as a fused generic RTDL primitive.

This is deliberately not:

- a Triton-first product claim;
- a true-zero-copy claim;
- a broad RT-core speedup claim;
- a whole-app speedup claim;
- a paper-reproduction claim;
- a release/tag authorization.

## Delivered In v2.5

| Area | Delivered status |
| --- | --- |
| App-agnostic native engine boundary | Native engine remains app-agnostic; no app-specific native customization is authorized. |
| Primitive-first execution policy | Goal2978 machine-encodes primitive-first native RTDL for exact fused continuations. |
| Typed hit-stream and payload handoff | Generic hit-stream and typed primitive-payload handoff scaffolding exists with claim boundaries. |
| Partner-continuation protocol | Partner continuations exist for explicit app/user choice where native primitives do not fuse the continuation. |
| Same-contract partner choice | Goal2979 shows partner choice is evidence-driven: RayDB uses fused RTDL, DBSCAN uses RT grouped stream + partner continuation, vector sum picks the measured CuPy path. |
| Canonical packet and triage | Current packet evidence has passed prior 7-app and 10-app triage gates, with zero active performance targets in the tracked packet. |
| Governance/provenance | Readiness packet, blocked-action list, runtime seam trace, conformance snapshot, and claim-boundary tests remain fail-closed. |

## Not Delivered In v2.5

| Area | Explicit boundary |
| --- | --- |
| Full partner-neutral composition | Goal2980 scopes it out; v2.5 has scaffolding, not an end-to-end delivered multi-partner residency layer. |
| True zero-copy | Runtime traces and same-pointer observations are evidence only; true zero-copy wording remains blocked. |
| Automatic Triton selection | Triton is never auto-selected merely because it is present. |
| Triton performance win | Goal2979 reinforces that Triton can lose; v2.5 is not a Triton-speed claim. |
| Whole-app speedup | No general whole-app speedup wording is authorized. |
| Broad RT-core speedup | App/row-specific internal evidence exists, but broad public RT-core wording remains blocked. |
| Paper reproduction | Benchmark apps are research-informed, not paper-reproduction claims. |
| Package-install promise | Package-install wording remains blocked. |
| v3.0 residency pipeline | Native device-resident end-to-end pipeline and CUDA-Graph residency work are future v3.0/v2.x research. |

## Evidence Summary

| Evidence | Status |
| --- | --- |
| Goal2978 primitive-first policy | `accept` by local tests; readiness indexed. |
| Goal2979 representative same-contract gate | `pass`; RTX 4000 Ada; current source commit `6fd7be7c9ab20b2128634cfffb6e673caf2c8824`. |
| Goal2980 neutral-seam scope-out decision | `accept`; full partner-neutral composition explicitly not delivered. |
| Goal2977 second-architecture packet attempt | Useful RTX 4000 Ada evidence, but not a complete canonical release packet because the large Barnes-Hut Embree baseline was bounded/killed. |
| Goal2973 current packet with toolchain scope | Prior clean 7-app packet and toolchain-scope metadata, still internal evidence only. |
| Goal2969 10-app triage | Prior 10-app triage passed with zero active performance targets. |

## External Review Questions

External reviewers should answer these questions directly:

1. Does Goal2981 accurately state the v2.5 delivered/not-delivered boundary?
2. Is the Goal2978 primitive-first policy consistent with Goal2979 evidence?
3. Is Goal2980's C-3b scope-out decision honest enough, or must v2.5 fix the neutral seam before any release packet?
4. Are any phrases in Goal2981 overclaiming release readiness, public speedup, whole-app speedup, true zero-copy, broad RT-core speedup, automatic Triton selection, or paper reproduction?
5. What work remains before a user-requested v2.5 release packet can be written?

## Release Boundary

Goal2981 does not authorize:

- v2.5 release or release tag action;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- package-install wording;
- Triton preview auto-selection;
- paper reproduction claims;
- app-specific native engine customization.

The next valid action is external review of Goals 2978-2981. A release packet
may only be prepared if the user explicitly requests release preparation after
that review, and final release still requires the project's fresh 3-AI consensus
rule.

## Validation

```text
PYTHONPATH=src;. py -3 -m py_compile src\rtdsl\hit_stream_handoff.py src\rtdsl\__init__.py src\rtdsl\v2_5_internal_readiness.py tests\goal2981_v2_5_closeout_positioning_and_external_review_packet_test.py
PYTHONPATH=src;. py -3 -m unittest tests.goal2981_v2_5_closeout_positioning_and_external_review_packet_test tests.goal2980_neutral_seam_scope_out_closeout_decision_test tests.goal2979_representative_same_contract_gate_after_primitive_first_policy_test tests.goal2978_primitive_first_v2_5_closeout_policy_test tests.goal2806_v2_5_internal_readiness_packet_test
```
