# Goal 157: Fresh-Clone External Agent Acceptance

## Why

Before the final v0.2 tag, the repo should pass one more independent
acceptance-style test:

- multiple agents
- fresh Linux clones
- no reuse of the already-prepared working tree
- each agent writes and runs its own RTDL program
- each agent reports whether it could finish end-to-end

This is different from the earlier internal audits and the Antigravity reports.
It is meant to answer a release question:

- can an independent agent land on a clean Linux clone and successfully build,
  author, run, and explain a small RTDL program without relying on our in-tree
  hand-holding?

## Scope

- define a fresh-clone Linux external acceptance task
- define at least three independent agent work items
- require each agent to author its own RTDL program
- require each agent to produce a structured report

## Acceptance

- the handoff tells agents to use a totally new Linux clone
- the handoff gives at least three independent authored-program tasks
- the handoff requires a structured written report
- the handoff is explicit about platform and backend honesty boundaries

## Important Boundary

This goal prepares the external acceptance task.

It does **not** claim the external acceptance test is complete until the
returned agent reports are collected.
