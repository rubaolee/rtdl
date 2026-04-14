# Goal 366 Report: v0.6 second real dataset plan

## Summary

After Goal 365, the best next move is to diversify the real-data line instead
of pushing `wiki-Talk` alone.

## Recommendation

Choose:
- `graphalytics_cit_patents`

as the second real graph family for the `v0.6` bounded evaluation line.

## Why this is the right next move

### 1. It adds dataset diversity

Current real-data evaluation is entirely on:
- `wiki-Talk`

That is enough to establish the opening graph line, but not enough to show that
the current bounded results are not overly shaped by one dataset family.

### 2. It is already in the repo’s dataset metadata

The existing `graph_datasets.py` candidate list already includes:
- `graphalytics_cit_patents`

with bounded reference metadata:
- directed graph
- about `3.77M` vertices
- about `16.5M` edges

### 3. It stays aligned with the current workload pair

For `v0.6`, the opening workload pair is still:
- `bfs`
- `triangle_count`

`cit-Patents` is a good next BFS-family dataset immediately because it is a
large real directed graph.

For triangle count, the first bounded use should still preserve the current
simple-undirected transform discipline:
- symmetrize if needed
- drop self-loops
- canonical undirected dedupe

### 4. It is more valuable than more `wiki-Talk` alone

Another same-dataset scale jump would give less new information than a second
real graph family.

## First bounded-use recommendation

### BFS

Start with:
- a bounded directed edge cap on `graphalytics_cit_patents`

### Triangle count

Start with:
- a bounded simple-undirected transformed slice
- explicit report language that Python remains the truth path, not necessarily
  the practical timing baseline

## Non-goals

- full `cit-Patents` closure
- immediate paper-scale reproduction
- multiple new datasets in the same slice
- new backend work
