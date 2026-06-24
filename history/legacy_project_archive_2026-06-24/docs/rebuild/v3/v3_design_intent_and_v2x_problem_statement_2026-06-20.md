# V3 Design Intent And V2.x Problem Statement

Status: active rebuild authority, 2026-06-20.

This document answers the release-owner question: why does V3 exist, and what
V2.x problem must it solve before it can be trusted as a major language
version?

## Core Answer

V3 exists to turn RTDL from a capable research line into a usable language
release.

V2.x proved that RT-shaped non-graphics workloads can be expressed and executed
through RTDL routes. It did not yet give a serious user one clean, dependable
answer to:

```text
What can I safely build with RTDL today, which backend do I choose, and what
evidence supports that choice?
```

V3 must answer that question without making the user read project history,
archived benchmark notes, or internal release debates.

## V2.x Problems V3 Must Fix

V2.x left five user-facing problems.

1. Fragmented language story

   The pieces existed, but the user had to infer the programming model from
   benchmark apps, reports, and historical notes. A major version cannot ask
   users to reconstruct the language from archaeology.

2. Unclear current truth

   Old reports, tutorial tracks, and experiment notes were too close to the
   front door. Users could mistake historical claims for current guarantees.

3. Backend and partner uncertainty

   Embree, OptiX, NumPy/CuPy/Numba, and app-specific benchmark routes appeared
   in many places, but the release surface did not consistently tell users
   which choices were supported, which were experimental, and which were
   blocked by toolchain issues.

4. Evidence not tied tightly enough to claims

   V2.x had useful benchmark evidence, but a user-facing claim needs exact row
   identity, environment, command, artifact, and classification. A broad claim
   without a row-level gate is not acceptable for V3.

5. Too much app-author burden

   A user should not need to write a custom native engine for every serious
   application. V3 must demonstrate reusable RTDL contracts for serious
   RT-shaped workloads, or it is not solving the language problem.

## V3 Must Be More Than An Experiment

V3 is acceptable only if it behaves like a release a user can learn and use:

- one front door;
- one current tutorial path;
- one explicit programming contract;
- serious runnable examples;
- row-level performance evidence against the V2.x line where performance is
  claimed;
- clear backend and partner rules;
- explicit non-claims;
- no active V4 or historical material promoted as current user guidance.

If V3 cannot meet this bar, the correct action is not to polish wording. The
correct action is to keep V3 unpublished, repair or remove failed rows, and
rebuild the user surface from passing evidence only.

## What Counts As Solving The User Problem

V3 solves the user problem only when a new app author can do all of the
following:

1. Install or enter the source tree and run a sanity check.
2. Read a short tutorial and understand the RTDL loop.
3. Select a supported backend or partner without guessing from history.
4. Run at least one serious workload with an exact M7-qualified row-scoped
   contract after aggregate release authorization.
5. Inspect the exact artifact behind any performance statement.
6. Know which workloads are not ready, and why.

This is the difference between a research branch and a major language version.

## Evidence Rule

No V3 performance wording is allowed unless it is backed by:

- the compared revision or tag for the V2.x baseline;
- the compared revision or source state for V3;
- the GPU/driver/toolchain environment;
- exact commands;
- raw logs and summary artifacts;
- row classification;
- a statement of what the row does and does not prove.

Rows must be classified as one of:

- `m7-qualified-row-scoped`;
- `needs-repair`;
- `environment-blocked`;
- `internal-only`;
- `removed`.

Only M7-qualified row-scoped rows may return to tutorials, examples, and public
performance wording after aggregate release authorization.

## Current Decision

The current rebuild decision is:

```text
Do not claim V3 is released. First prove whether current V3 materially improves
the V2.x user problem on serious pod benchmarks. If it does not, V3 must be
repaired or rebuilt before publication.
```

Goal-level decision audit:

1. Did I make a foolish decision?

   Yes, earlier work treated a polished V3/V4 release surface as stronger than
   it was.

2. What actions made it foolish?

   It mixed current and future scope, let old docs remain too close to the
   front door, and did not force every claim through a fresh V2.x comparison.

3. Was there another path?

   Yes: quarantine old material first, reconstruct the V3 user problem, then
   use pod evidence as the release gate.

4. What different path is now being used?

   V3 is being rebuilt from evidence. Current work is limited to V3 versus
   V2.x, row classification, repair decisions, and republishing only proven
   user material.
