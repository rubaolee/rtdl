# Goal4254 v2.10 Public Claim Wording Candidate

Date: 2026-06-09
Status: candidate wording for review, not release authorization

## Purpose

Goal4254 proposes exact public wording that could be used in a future v2.10
release packet if the user requests release and the required multi-AI consensus
accepts the wording. This file is deliberately narrow: it separates what can be
said from what cannot be said.

## Candidate Short Description

RTDL v2.10 is a Python-hosted ray-tracing DSL/runtime for non-graphical
workloads. It lets users express traversal-heavy work through generic RTDL
primitives, choose an explicit backend such as the Python reference runner,
Embree, or OptiX, and compose the result with user-chosen Python partners such
as Numba or CuPy where a benchmark needs custom continuation logic.

The native engine is a generic, app-agnostic native engine. Application
semantics live in Python examples, benchmark front doors, partner continuations,
or user code.

## Candidate Evidence Statement

The current internal evidence packet for v2.10 includes:

- a 10-app benchmark front-door rehearsal on an RTX 4000 Ada pod;
- second-level timing evidence for all ten promoted benchmark apps;
- dedicated long-repeat evidence for RayJoin-style contract splits;
- dedicated long-repeat evidence for the formerly short Hausdorff,
  contact-manifold, and triangle-counting rows;
- a public-doc claim-boundary scan with zero hard blockers;
- a target map whose release and speedup authorization flags remain
  structurally false until a formal release packet is reviewed.

This evidence supports source-tree development claims about the current RTDL
runtime surface. It does not by itself authorize package-release or broad
performance marketing.

Short evidence wording: ten promoted benchmark front doors pass on an RTX 4000 Ada pod.

## Candidate Allowed Claims

The following claims are candidates for release wording after review:

1. RTDL v2.10 exposes a Python+partner+RTDL programming model over a generic,
   app-agnostic native engine.
2. Users choose the backend and partner explicitly; RTDL does not hide an
   automatic partner/backend dispatcher behind public examples.
3. The promoted benchmark surface currently includes ten paper-motivated
   benchmark apps used to stress RTDL language/runtime design.
4. Current NVIDIA/OptiX internal evidence shows all ten promoted benchmark front
   doors pass on an RTX 4000 Ada pod.
5. Current internal evidence includes second-level timing for all ten promoted
   benchmark apps.
6. For selected RT-heavy contracts, reviewed artifacts show strong OptiX
   benefits over same-contract CPU or partner baselines.
7. RayJoin-style evidence is contract-split: one-shot bounded PIP, repeated
   PIP, LSI, and overlay active-count are reported separately rather than
   collapsed into one whole-app RayJoin number.
8. RT-DBSCAN-style evidence is profile-aware: the unblocked single-pass grouped
   stream is the current default shape, while blocked grouped stream remains
   explicit/profile-specific.
9. Prepared-session reuse is explicit and caller-owned.
10. Benchmark examples are reconstruction instruments for RTDL design, not
    authors-code reproductions of the cited papers.

## Claims That Must Not Be Made

The following wording remains blocked:

1. RTDL v2.10 is released as a package-install product.
2. RTDL v2.10 makes every user program faster.
3. RTDL v2.10 provides a broad RT-core speedup guarantee.
4. RTDL v2.10 provides whole-application acceleration for every benchmark.
5. RTDL beats RayJoin as a full paper system.
6. RTDL reproduces the full authors-code results of RayJoin, X-HD, RTNN,
   RT-DBSCAN, or other papers.
7. RTDL provides a general true-zero-copy product guarantee.
8. RTDL automatically chooses the best backend or partner.
9. RTDL has AMD/HIPRT performance evidence without an actual AMD hardware run.
10. RTDL contains app-specific native-engine logic for benchmark apps.

## Candidate Front-Page Paragraph

RTDL v2.10 is used from the source tree with `PYTHONPATH=src:.`. It is a
Python-hosted RT DSL/runtime for non-graphical workloads, built around generic
ray-tracing primitives and explicit user-chosen backends/partners. Current
internal evidence covers ten promoted benchmark front doors on NVIDIA/OptiX and
keeps public claims scoped by contract and artifact. Do not read v2.10 as a
package-install promise, universal speedup promise, whole-app acceleration
promise, paper-reproduction claim, automatic partner-selection claim,
true-zero-copy product guarantee, or AMD/HIPRT performance claim.

## Candidate Benchmark Wording

The benchmark apps are not fixed RTDL features or app-specific native-engine
paths. They are design-pressure workloads used to test whether generic RTDL
primitives, explicit prepared execution, and user-chosen partners can express
serious non-graphical ray-tracing workloads. Performance statements must cite
the exact contract and artifact, not just the app name.

## Boundary

This document is a wording candidate only. It does not authorize release,
public speedup wording, whole-app acceleration wording, broad RT-core wording,
RTDL-beats-RayJoin wording, paper-reproduction wording, package-install wording,
true-zero-copy wording, automatic partner/backend selection, AMD/HIPRT
performance wording, or app-specific native-engine logic.
