# RTDL Development Reliability Process

This document explains the workflow currently used in RTDL and why that workflow improves project reliability, traceability, and staged delivery quality.

## 1. Purpose

RTDL is not a one-off script project. It is a staged research and systems project that spans:

- DSL design
- compiler IR and lowering
- multiple runtime backends
- dataset handling
- benchmarking and figure generation
- multi-agent review

Because of that, project reliability cannot depend only on "the code runs." It also needs a repeatable development and validation process.

The goals of this process are:

- make each stage explicit
- ensure every implementation gets independent review
- ensure every revision has a reason
- keep every conclusion traceable
- keep `main` as a verified baseline rather than an experimental scratch branch

## 2. Core principles

The current RTDL workflow is built on these principles:

1. Define the goal before writing code
   The default mode is not "code first and clarify later."

2. Review the goal before implementation
   The goal, scope, and acceptance boundary should be checked by another agent first.

3. Implementation must produce validation evidence
   If there are no tests, no runnable evidence, and no example programs, the feature is not considered complete.

4. Revisions must respond to review findings
   Code changes are not treated as arbitrary iteration. They are tied to review conclusions.

5. Consensus is required to close a goal
   If Codex and the reviewer have not converged on the outcome, the goal is not closed.

6. History must be archived
   Every round should remain traceable: goal, review, response, revision, and final closure.

## 3. Standard workflow

RTDL currently follows this standard workflow.

### Step 1: Define the goal

Each round starts with a specific goal, for example:

- add a new workload
- finish a backend execution path
- freeze the Embree baseline contract
- generate an evaluation report and figures

The goal must state at least:

- what problem it solves
- what is in scope
- what is explicitly out of scope
- what counts as success

This helps:

- prevent goal drift
- avoid mixing unrelated work into one round
- make later review precise instead of subjective

### Step 2: Ask another agent to review the goal

Before coding starts, another agent reviews the goal definition.

In this project that reviewer is usually:

- Gemini
- or another Codex instance

The reviewer is not asked to immediately help implement it. The first review is about:

- whether the goal is sound
- whether the scope is too broad or too narrow
- whether the acceptance conditions are adequate
- whether key risks are missing
- how the reviewer intends to verify completion

This matters because:

- design mistakes are cheapest to fix before implementation
- it prevents finishing code for a goal that was poorly defined in the first place

### Step 3: Implement within the agreed boundary

Implementation starts only after the goal and review approach are agreed.

The implementation rules are:

- stay within the current goal boundary
- add tests, examples, and documentation together with the code
- prefer executable evidence over static code only

For example, a workload-expansion goal usually requires:

- DSL API updates
- IR / lowering updates
- CPU semantics
- Embree runtime support
- unit tests
- integration tests
- example programs
- documentation

### Step 4: Run validation

Implementation is not enough by itself. Validation must run after the code is written.

Validation typically includes:

- unit tests
- integration tests
- authored example runs
- CPU vs Embree output comparison
- benchmark / summary / figure pipeline checks when relevant

The purpose is to ensure:

- the code does not just exist, it executes
- new features do not break existing ones
- there is concrete evidence of backend consistency

## 4. Why the CPU reference path matters

One of the strongest current reliability mechanisms in RTDL is the dual execution path:

- `rt.run_cpu(...)`
- `rt.run_embree(...)`

Here:

- `run_cpu(...)` is now the native C/C++ oracle path, while `run_cpu_python_reference(...)` preserves the old Python semantics for regression checks
- `run_embree(...)` is the real local native backend

That means the project does not rely on one implementation alone.

A stronger validation pattern is:

1. take the same DSL kernel
2. run it on the CPU reference
3. run it on the Embree backend
4. compare the outputs

This parity model improves reliability because:

- one backend can validate another
- new workload semantics can be stabilized first on CPU
- a large amount of functional validation is possible on a Mac before the NVIDIA machine arrives

## 5. Step 5: Independent implementation review

After implementation and validation, another agent reviews the implementation itself.

The implementation review focuses on:

- correctness blockers
- consistency with the original goal
- semantic mismatches
- over-claims
- whether tests cover the real risk points
- whether the current boundary is documented honestly

If issues are found, the process continues with:

- Codex response
- implementation revision
- another review pass

That means RTDL uses multi-round convergence rather than one-pass approval.

## 6. Step 6: Archive the round after consensus

When a goal is considered complete, the result is not just a commit. The round is archived in `history/`.

Archived material includes:

- the goal definition
- pre-implementation review
- implementation report
- external review reports
- Codex responses / rebuttals
- final consensus note
- history dashboard entries

In the current project, the archive layers include:

- `history/history.db`
- `history/revision_dashboard.html`
- `history/revision_dashboard.md`
- `history/revisions/<round>/...`

This matters because it makes every round auditable. It becomes possible to answer:

- why a design choice was made
- what a reviewer objected to
- how the implementation changed
- how the goal was finally closed

## 7. Step 7: Only push to main after the loop is closed

The current RTDL rule is:

Only push to `main` after all of the following are true:

- the goal is explicit
- review consensus exists
- implementation is complete
- validation passes
- revisions are complete
- history is updated

The result is:

- `main` stays as a staged verified baseline
- transient experimental states are not treated as official project state

## 8. How this process improves reliability

This workflow improves project reliability in several distinct ways.

### 8.1 It reduces goal-level errors

Many projects fail not because the code is incorrect, but because the goal itself was weakly defined.

By defining the goal first and reviewing it first, RTDL reduces the chance of:

- building the wrong thing
- missing a required deliverable
- choosing a scope too large to finish
- choosing a scope too small to matter

### 8.2 It reduces hidden implementation errors

If a project has only one implementation path and no reference path, many errors remain invisible.

RTDL currently uses:

- CPU reference execution
- Embree backend execution
- parity testing

That creates a stronger cross-checking model.

### 8.3 It reduces single-reviewer bias

A single agent can:

- miss an issue type
- misjudge the boundary
- become overconfident

By involving Gemini or another Codex instance, the process gains at least:

- a primary implementer
- an independent reviewer

That is not formal verification, but it is significantly stronger than a one-agent closed loop.

### 8.4 It reduces documentation drift

In the current workflow, docs, examples, and tests are usually advanced together with the feature.

That reduces a common failure mode:

- the code changed
- the documentation still describes old behavior

This matters especially for a DSL project, because the language must be usable by both humans and agents.

### 8.5 It preserves historical reasoning

Research projects often lose an important asset:

- the reasoning behind earlier design choices

By archiving each review and revision round, RTDL turns that history into an explicit project asset rather than leaving it hidden in chat logs or memory.

## 9. Current limitations of the process

This workflow improves reliability, but it does not guarantee absolute correctness.

Current limits still include:

1. The reference semantics could still be wrong
   If `run_cpu(...)` is flawed, parity only proves that two backends match, not that the geometry is mathematically exact.

2. The current semantics are still `float_approx`
   So "correct" currently means correct relative to the current floating-point semantics, not exact computational geometry.

3. Gemini CLI is not fully reliable
   Some reviews require retries, narrower prompts, or archived snapshots instead of direct file inspection.

4. The NVIDIA/OptiX backend is now a real execution path, but it is still in an early bounded-validation stage
   So the current process strengthens both the CPU/Embree system and the first GPU path, but does not replace broader future NVIDIA runtime validation on real workloads.

So the accurate statement is:

This workflow substantially improves system reliability at the current stage, but it does not remove the need for future real backend validation on NVIDIA hardware.

## 10. Why this matters for the current phase

For RTDL specifically, the biggest value of this process is that it allows the project to stabilize:

- the language
- the IR
- the CPU reference
- the Embree baseline
- the evaluation pipeline

before the project enters the OptiX / NVIDIA phase.

That means when the NVIDIA backend work begins, the problem becomes narrower:

- backend specialization
- GPU runtime integration

rather than:

- inventing the language
- inventing the backend
- debugging semantics

all at the same time.

## 11. Summary

The current RTDL reliability model does not come from one technique. It comes from a full process:

1. define the goal
2. review the goal
3. implement within the agreed scope
4. run tests and examples
5. perform independent implementation review
6. revise until consensus
7. archive the round
8. only then push to main

The value of this process is:

- every step is explainable
- every conclusion has evidence
- every revision has a reason
- the project moves forward as a verifiable research-engineering system

For the current RTDL stage, that process is one of the main reasons the project has moved from "idea" to "credible executable prototype."
