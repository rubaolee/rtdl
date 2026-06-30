# Goal2486 Robot Collision Continuous Feasibility

Date: 2026-05-21

Status: Goal2486 is complete.

Decision: defer implementation.

## Scope

Goal2486 studies whether the current robot-collision campaign should implement
continuous or swept collision now.

It should not. Continuous collision is a separate semantic layer from the
Goal2481 discrete sampled segment-probe contract. Implementing it now would
either import application policy into the native engine or require a new generic
primitive that has not been scoped.

## Candidate Directions

The viable directions are:

- sampled transforms over time;
- swept spheres/capsules;
- conservative interval/bounds primitive;
- app-level continuation over discrete RTDL queries.

The lowest-risk near-term direction is app-level continuation over discrete
RTDL queries. It can reuse the existing prepared scene and changing query batch
model while preserving Python ownership of motion policy.

Swept spheres/capsules and conservative interval/bounds primitives may be good
RTDL language/runtime work later, but they need a separate generic contract,
separate parity fixtures, and separate Embree/OptiX semantics.

## Boundary

No native ABI is added in Goal2486. Python owns continuous-collision policy,
including interpolation, sampling density, conservative expansion, and what
counts as contact.

Continuous collision is not part of Goal2484/2485 performance claims. The
current prepared benchmark remains a discrete sampled probe benchmark.

Blocked claims:

- paper reproduction remains blocked;
- exact swept contact remains blocked;
- public speedup wording remains blocked;
- native robot, link, pose, planner, or collision APIs remain blocked.

## Decision

Continuous/swept support is a v3.0-or-later candidate unless a smaller generic
primitive is separately proposed and reviewed before then.

For this campaign, Goal2487 should close the project with:

- the discrete prepared scene plus changing query batch value recorded;
- the sampled-probe limitation explicit;
- continuous/swept work deferred.
