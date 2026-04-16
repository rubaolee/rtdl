# RTDL v0.7 Branch Tag Preparation

Date: 2026-04-15
Status: hold

## Current Decision

Do not tag `v0.7` yet.

## Why

- the bounded DB line is now release-gated through Goal 430
- Goal 431 packages the branch surface honestly
- the user has explicitly indicated that multiple additional goals remain before
  a final release decision

## What Is Ready

- bounded DB kernel surface
- cross-engine correctness closure on Linux
- bounded Linux performance package with PostgreSQL included
- public examples/tutorials aligned with the achieved backend surface

## Hold Condition

Keep `v0.7` as a branch line until later goals are complete and a new final
release decision is made.
