# Goal 361 Report: v0.6 audit adoption and evaluation correction

## Summary

This slice adopts the detailed Gemini audit and the Claude second-leg review as
active engineering feedback.

## What was corrected

### PostgreSQL timing methodology

`src/rtdsl/graph_eval.py` now separates:
- `postgresql_seconds`
  - query-only timing
- `postgresql_setup_seconds`
  - table preparation / load / index / analyze timing

This fixes the main audit defect in the earlier `v0.6` graph evaluation line.

### Additional low-risk code cleanups

- removed redundant condition in PostgreSQL triangle-count SQL
- removed the extra unreported Python BFS call in
  `bfs_baseline_evaluation(...)`
- replaced the `assert` in `grid_graph(...)` with an explicit runtime error
- removed unreachable dead-code branch in `validate_csr_graph(...)`

## Corrected Linux PostgreSQL numbers

### Goal 355 synthetic bounded Linux graph eval

- `bfs`
  - PostgreSQL query: `0.001259607 s`
  - PostgreSQL setup: `0.012505270 s`
- `triangle_count`
  - PostgreSQL query: `0.001078883 s`
  - PostgreSQL setup: `0.019379521 s`

### Goal 357 / 358 bounded real-data BFS on `wiki-Talk`

- PostgreSQL query: `0.000543500 s`
- PostgreSQL setup: `11.957648676 s`

### Goal 359 bounded real-data triangle count on `wiki-Talk`

- PostgreSQL query: `0.237828660 s`
- PostgreSQL setup: `3.265396886 s`

## Test status

Focused local graph suite after the fixes:

```text
python3 -m unittest \
  tests.goal352_v0_6_graph_eval_test \
  tests.goal356_v0_6_graph_dataset_prep_test \
  tests.goal357_v0_6_wiki_talk_bfs_eval_test \
  tests.goal359_v0_6_wiki_talk_triangle_count_eval_test \
  tests.claude_goal353_v0_6_graph_review_test
Ran 72 tests
OK
```

Expanded focused graph suite:

```text
python3 -m unittest tests.claude_goal353_v0_6_graph_review_test \
  tests.goal345_v0_6_bfs_truth_path_test \
  tests.goal346_v0_6_triangle_count_truth_path_test \
  tests.goal348_postgresql_bfs_baseline_test \
  tests.goal349_postgresql_triangle_count_baseline_test \
  tests.goal350_v0_6_bfs_oracle_test \
  tests.goal351_v0_6_triangle_count_oracle_test \
  tests.goal352_v0_6_graph_eval_test \
  tests.goal356_v0_6_graph_dataset_prep_test \
  tests.goal357_v0_6_wiki_talk_bfs_eval_test \
  tests.goal359_v0_6_wiki_talk_triangle_count_eval_test
Ran 90 tests
OK
```

Linux focused graph suite after sync:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal352_v0_6_graph_eval_test \
  tests.goal356_v0_6_graph_dataset_prep_test \
  tests.goal357_v0_6_wiki_talk_bfs_eval_test \
  tests.goal359_v0_6_wiki_talk_triangle_count_eval_test
Ran 13 tests
OK
```

## Effect

The bounded `v0.6` graph line is stronger after adoption than before:
- better tested
- more honest in its evaluation claims
- no longer relying on the flawed combined PostgreSQL timing interpretation
