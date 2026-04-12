# Goal 258: v0.5 Paper-Consistency Charter

## Purpose

Open the `v0.5` line with a precise charter focused on paper/implementation
consistency.

The central goal is not "more features" in the abstract. The central goal is:

- make RTDL capable of honestly reproducing the paper-related experiment lines
  it points at, especially the RTNN nearest-neighbor line

## Core v0.5 Question

Can RTDL move from:

- a released nearest-neighbor `v0.4.0` line that is correct and useful

to:

- a `v0.5` line that can support paper-faithful or near-paper-faithful
  reproduction of the RTNN-style experiment package

## v0.5 Primary Deliverables

1. A true 3D nearest-neighbor public surface.
2. A paper-consistent KNN contract where needed.
3. Dataset packaging and documented acquisition paths for the paper-aligned
   benchmark suite.
4. Baseline-library comparison harnesses beyond the current PostGIS / SciPy
   story.
5. Experiment scripts and reports that distinguish:
   - exact reproduction
   - close reproduction
   - RTDL-inspired extensions

## In Scope

### 1. 3D nearest-neighbor workload line

`v0.5` should add or evolve the nearest-neighbor public surface so that paper
evaluation stories using 3D point data are structurally possible.

Minimum expectation:

- 3D point support for nearest-neighbor workloads
- CPU/oracle truth path
- Embree
- OptiX
- Vulkan

### 2. Bounded-radius KNN consistency

If the target paper semantics require both:

- search radius
- maximum neighbor count

then `v0.5` should expose that contract directly instead of forcing the paper
story through the current `k`-only `knn_rows` shape.

### 3. Paper-aligned dataset layer

`v0.5` should provide documented, reproducible acquisition or preparation flows
for the datasets needed by the paper-consistency story.

This likely includes:

- KITTI-derived point sets
- Stanford 3D scan point sets
- N-body / Millennium-style point sets

### 4. Baseline-library harnesses

`v0.5` should decide explicitly which paper baselines are required and which
are infeasible.

Target set for evaluation:

- cuNSearch
- FRNN
- PCLOctree
- FastRNN

If any are impossible to package or validate honestly, the repo should say so
explicitly rather than silently dropping them.

### 5. Experiment and report discipline

Every `v0.5` experiment report should label results as one of:

- exact reproduction
- bounded reproduction
- RTDL extension

This keeps paper-consistency claims honest.

## Non-Goals

The `v0.5` line is **not** primarily about:

- front-page redesign
- more visual-demo polish for its own sake
- unbounded general-rendering claims
- chasing every new GPU/backend optimization before the paper-consistency story
  is structurally sound

## Release Standard

`v0.5` should not be called released until the repo can demonstrate:

1. structurally correct paper-aligned nearest-neighbor surfaces
2. documented datasets and baselines
3. reproducible experiment scripts
4. explicit honesty about any still-missing paper elements

## First Planned Goal Groups

1. `v0.5` surface design
   - 3D points
   - nearest-neighbor contract updates

2. correctness path
   - Python/oracle truth for the new surfaces
   - regression tests across backends

3. dataset and harness layer
   - point-cloud ingest
   - baseline-library adapters

4. experiment layer
   - paper-aligned benchmark scripts
   - reproduction matrices

5. release/audit layer
   - exact-vs-bounded reproduction labeling
   - saved multi-AI review trail

## Success Condition

`v0.5` is successful if, by the end of the line, RTDL can honestly say:

- which RTNN-style experiments it reproduces exactly
- which it reproduces approximately
- which remain unsupported

and those claims are backed by runnable code and saved audit artifacts.
