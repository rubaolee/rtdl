# Goal 357: v0.6 wiki-Talk BFS Bounded Evaluation

## Why this goal exists

The repo now has:

- a bounded real-data preparation path
- a live Linux evaluation harness

The next honest step is to run the first bounded BFS evaluation on a real graph
dataset rather than staying on synthetic cases only.

## Scope

In scope:

- SNAP `wiki-Talk`
- bounded edge-capped BFS case
- Linux evaluation against:
  - Python truth path
  - compiled CPU/native oracle
  - PostgreSQL baseline when available

Out of scope:

- full `wiki-Talk` closure
- triangle-count on `wiki-Talk`
- large-scale benchmark claims

## Exit condition

This goal is complete when the repo has:

- a bounded `wiki-Talk` BFS evaluation report
- a saved external review
- a saved Codex consensus note
