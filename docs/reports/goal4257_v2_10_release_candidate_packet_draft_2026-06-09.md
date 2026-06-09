# Goal4257 v2.10 Release-Candidate Packet Draft

Date: 2026-06-09
Status: draft packet, not release authorization

## Purpose

Goal4257 assembles the first formal release-candidate packet draft for v2.10.
It is still a draft: it does not tag, publish, or authorize release. Its job is
to make the final decision surface explicit enough for a 3-AI consensus pass and
user release decision.

## Candidate Release Identity

| Field | Value |
| --- | --- |
| Candidate version label | `v2.10` |
| Candidate theme | Python+partner+RTDL over a generic app-agnostic native engine |
| Base pushed commit when this draft was written | `0d208ea6` |
| Latest runtime/perf evidence commit | `14dbb8e0` to `188e896e`, depending on report/test scope |
| Primary NVIDIA evidence hardware | RTX 4000 Ada |
| AMD/HIPRT release claim | not included |
| Package-install claim | not included |

## Included Evidence

| Evidence Area | Required Source |
| --- | --- |
| Ten-app current front-door rehearsal | Goal4235 |
| RayJoin dedicated long-repeat profile | Goal4239 |
| Short-row long-repeat refresh | Goal4243 |
| Short-row external reviews | Goal4246 and Goal4247 |
| Public-doc claim-boundary scan | Goal4248 |
| Current target map | Goal4249 |
| Post-docs pod validation | Goal4250 |
| Internal release-prep packet | Goal4251 |
| Internal release-prep external reviews | Goal4252 and Goal4253 |
| Public claim wording candidate | Goal4254 |
| Public claim wording external reviews | Goal4255 and Goal4256 |

## Candidate Release Claims

The release packet may use the Goal4254 wording candidate after final review.
The essential claims are:

1. RTDL v2.10 is a Python-hosted RT DSL/runtime for non-graphical workloads.
2. RTDL v2.10 uses generic RTDL primitives over an app-agnostic native engine.
3. Users choose backend and partner explicitly.
4. Current internal evidence covers ten promoted benchmark front doors on
   NVIDIA/OptiX.
5. Performance claims are contract-scoped and artifact-scoped.
6. Benchmark apps are design-pressure workloads, not authors-code
   reproductions.

## Claims Excluded From This Release Packet

This draft excludes:

- package-install product readiness;
- universal speedup;
- broad RT-core speedup guarantee;
- whole-application acceleration guarantee;
- RTDL-beats-RayJoin wording;
- full paper reproduction;
- true-zero-copy product guarantee;
- automatic backend/partner selection;
- AMD/HIPRT performance or parity wording;
- app-specific native-engine logic.

## Required Final Steps Before Release

| Step | Status | Notes |
| --- | --- | --- |
| Final Claude review of Goal4254 wording | done-with-boundary | Goal4255 accepted with three required wording fixes; those fixes are applied in Goal4254. |
| Final 3-AI release consensus over this exact packet | pending | Must include Codex plus two distinct external AI systems, not Codex+Codex. |
| User release decision | pending | Required before tag/publish. |
| Final pod validation at the exact release commit | pending | Should rerun the Goal4250-style release-prep slice after any final packet edits. |

## Current Readiness

If no AMD, package-install, universal speedup, whole-app acceleration,
true-zero-copy, or paper-reproduction claim is made, the current NVIDIA/OptiX
source-tree evidence appears internally coherent and close to release-candidate
quality.

The remaining work is governance and exact packet validation, not a known
NVIDIA measurement gap.

## Boundary

Goal4257 is a draft packet only. It does not authorize release, public speedup
wording, whole-app acceleration wording, broad RT-core wording,
RTDL-beats-RayJoin wording, paper-reproduction wording, package-install wording,
true-zero-copy wording, automatic partner/backend selection, AMD/HIPRT
performance wording, or app-specific native-engine logic.
