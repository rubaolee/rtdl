# RTDL AI Collaboration Workflow

This document explains how multiple AI agents are used together to build RTDL, review changes, revise plans, and decide when a goal is actually complete.

It is a project-process document, not a language or backend specification.

## 1. Why RTDL uses multiple AI agents

RTDL is not a single-layer project. It spans:

- DSL design
- compiler IR and lowering
- runtime backends
- dataset and benchmark pipelines
- reports, figures, and archived research evidence

For that kind of work, a single-agent workflow is too easy to overfit. One model can make a design mistake, over-claim a result, or miss a consistency issue that only becomes obvious when another reviewer looks at the same change from a different angle.

The project therefore uses a multi-agent process on purpose.

The goal is not “more AI for its own sake.” The goal is:

- independent review before implementation
- independent review after implementation
- explicit revision in response to findings
- traceable closure conditions

## 2. Current agent roles

The current RTDL process uses three practical roles.

### Codex

Codex is the main implementation driver in this repository.

Codex typically does the following:

- defines a goal and its scope
- writes or revises code
- updates tests, docs, reports, and decks
- runs validation
- writes responses to reviewer findings
- decides whether the repo state is ready for another review pass

Codex is responsible for keeping the working tree coherent.

### Gemini

Gemini is usually the secondary reviewer and consistency checker.

Gemini is typically asked to:

- review goal setup before implementation
- explain how it wants to verify the goal
- review the implemented result
- identify gaps, over-claims, semantic drift, or weak evidence
- provide a closure decision when the evidence is sufficient

Gemini is especially useful as a fast second opinion on whether the current scope is honest and complete.

### Claude

Claude is used as an additional reviewer or design critic, especially for:

- audit-style reviews
- plan criticism
- narrower correctness/performance comparison goals
- final closure checks on important rounds

Claude does not need to be involved in every small step, but when it is used, its role is to challenge assumptions and improve the technical wording of the closure.

## 3. Standard collaboration loop

The current collaboration loop is:

1. Define the goal.
   Codex writes the goal, scope, deliverables, and acceptance bar.

2. Get pre-implementation review.
   Gemini, Claude, or another Codex instance reviews the goal before code changes are accepted.

3. Revise the goal if needed.
   If the reviewer finds scope or evidence problems, Codex adjusts the plan first.

4. Implement the goal.
   Codex updates code, tests, docs, reports, and generated artifacts.

5. Run validation.
   Codex gathers runnable evidence: tests, examples, parity checks, reports, figures, or benchmark output.

6. Get implementation review.
   Another agent reviews the changed state and decides whether the evidence supports closure.

7. Revise again if needed.
   Findings are answered directly, then the code or docs are updated and reviewed again.

8. Close only after consensus.
   A goal is treated as complete only when the required agents agree.

9. Archive the round.
   The prompts, reports, responses, and final result are saved into `history/`.

## 4. What “consensus” means in this project

Consensus does not mean every agent writes the same report.

In RTDL, consensus means:

- the agents agree on the final status of the goal
- major objections are resolved
- the repo wording matches the actual evidence
- the remaining limitations are documented honestly

Examples of valid closure states:

- complete
- complete for a narrower accepted slice
- canceled and superseded
- blocked pending environment or hardware

Consensus is about the final project state, not stylistic agreement.

## 5. What each round must produce

A serious RTDL round usually produces:

- a goal/spec note
- at least one external review
- a Codex response to findings
- code and doc changes
- validation evidence
- a final consensus note
- archived round metadata

That is why a completed RTDL goal is more than a merged commit.

## 6. How the agents divide responsibility

The project uses a simple division of labor:

- Codex owns implementation coherence
- Gemini owns secondary review pressure
- Claude owns deeper critique or audit-style pressure when included

This is intentionally asymmetric.

The project does not try to make every agent do every task equally. Instead, it uses different agents to create structured disagreement early enough that the repository can be revised before the result is published.

## 7. Why this improves reliability

This process improves reliability in several ways:

- scope mistakes are caught before coding
- claims are reviewed against evidence
- runtime behavior is checked against reference paths
- docs are revised when the code evolves
- historical reasoning is preserved

It also makes the repo more usable for future contributors because they can inspect not only what changed, but why the change was accepted.

## 8. Known limitations

This workflow is still constrained by agent tooling.

Current practical limitations include:

- Gemini CLI sometimes returns progress narration before the final answer
- Claude usage can be quota-limited
- some reviews are better at plan-level criticism than patch-level authorship tracking
- final closure can depend on which agent is available that day

Because of that, the project keeps the archive and consensus notes explicit. If one agent is unavailable, the repository can still record what happened and what remains provisional.

## 9. Current project policy

The current policy is:

- no important goal closes on one agent alone
- docs and reports should match the real implementation state
- completed goals should be archived before they are treated as baseline
- canceled goals should be marked honestly rather than left ambiguous

This is why the history dashboard, revision database, and round archives exist.

## 10. Relationship to the rest of the repo

This document complements:

- [development_reliability_process.md](/Users/rl2025/rtdl_python_only/docs/development_reliability_process.md)
- [rtdl_feature_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md)
- [v0_1_final_plan.md](/Users/rl2025/rtdl_python_only/docs/v0_1_final_plan.md)

Those documents describe what RTDL is, what it currently supports, and where it is going.

This document explains how the agents collaborate to move the project from one accepted state to the next.
