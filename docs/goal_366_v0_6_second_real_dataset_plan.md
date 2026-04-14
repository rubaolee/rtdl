# Goal 366: v0.6 second real dataset plan

## Why

The `wiki-Talk` line is now strong enough to stop being the only real-data
story.

Current state:
- BFS bounded real-data line is real and scaled through `1500000` directed
  edges
- triangle-count bounded real-data line is real and scaled through `250000`
  canonical undirected edges
- parity remains clean across Python/oracle/PostgreSQL

The next highest-value move is dataset diversity, not more same-dataset scaling.

## Scope

Pick the next bounded real dataset family for `v0.6` and explain why it is the
best next move after `wiki-Talk`.

Stay bounded:
- planning only
- no downloader implementation yet
- no new evaluation claims yet

## Candidate direction

The current best next candidate from the existing dataset metadata is:
- `graphalytics_cit_patents`

## Closure

Close when the repo has:
- a concrete second-dataset recommendation
- reasons for the choice
- an explicit first bounded-use plan for:
  - `bfs`
  - `triangle_count`
- explicit non-goals
