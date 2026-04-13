# RTDL v0.5 Pre-Release Plan

Date: 2026-04-12
Status: active pre-release work plan

This document defines the next pre-release phase for `v0.5`.

## Phase Goals

1. docs
2. code test
3. audit
4. external review
5. make the final release package

## 1. Docs

Before final release, the repo should have:

- a readable front door
- a clean docs index
- a clear `v0.5` support matrix
- a clear internal/external call-for-test path
- explicit backend/platform boundaries

Current status:

- mostly ready
- main recent hardening work is complete
- remaining doc work should now be release-facing polish, not more archive
  expansion

## 2. Code Test

Before final release, the repo should have:

- one explicit pre-release regression sweep
- one focused nearest-neighbor/runtime sweep
- one statement of what is and is not part of the release gate

Current status:

- broad regression coverage is strong
- the final pre-release test gate should now be written down and rerun as one
  intentional slice

## 3. Audit

Before final release, the repo should have:

- one final bounded release audit
- explicit treatment of remaining bounded areas
- no silent drift between README, support matrix, and release package

Current status:

- multiple strong audits already exist
- the remaining work is final synthesis, not first discovery

## 4. External Review

Before final release, the repo should have:

- one clean external review packet
- direct links to the exact docs and commands reviewers should use
- a clear place for criticism to land without confusing preview vs release

Current status:

- external audits exist
- the next pass should be a final pre-release review round, not open-ended
  exploration

## 5. Final Release-Making

Before final release, the repo should have:

- final release statement
- final support matrix
- final audit report
- final tag-preparation note

Current status:

- not yet done
- this is the work that should happen after the code-test and audit pass closes

## Honest Summary

`v0.5` is no longer in the "prove the backend line exists" phase.

The pre-release phase is now:

- tighten the docs
- rerun the intended release-gate tests
- run the final audits and external review
- then publish the final release package
