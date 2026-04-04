# Goal 55 Full Test Surface Closure

## Objective

Strengthen the project test surface so the repo has a clearer and more complete
verification story across:

- unit tests
- integration tests
- system tests

This goal is about test coverage and test structure, not new backend features.

## Why This Goal

The repo already has a substantial test suite, but the current surface is still
uneven:

- many regression tests exist, but system-level acceptance is not organized as a
  single explicit matrix
- backend coverage is stronger for Embree than for the rest of the stack
- several acceptance-critical scripts and workflows still rely more on
  goal-specific tests than on a consolidated release-style verification layer

Before expanding the bounded reproduction program further, the test surface
should be made more explicit, complete, and easier to trust.

## Scope

In scope:

- inventory the current test suite
- classify tests into:
  - unit
  - integration
  - system
- identify critical gaps in backend, script, and acceptance coverage
- add missing high-value tests
- define a canonical verification matrix and command set
- verify the final suite

Out of scope:

- new paper-family acquisition or reproduction work
- major backend redesign
- rewriting archived historical reports

## Acceptance

Goal 55 is accepted only if:

1. the current suite is inventoried and classified
2. critical missing tests are added
3. system-test coverage for accepted bounded packages is explicit
4. a canonical verification command set is documented
5. the resulting suite passes
6. at least 2 AIs approve before publication
