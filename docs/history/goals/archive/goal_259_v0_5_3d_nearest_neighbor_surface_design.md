# Goal 259: v0.5 3D Nearest-Neighbor Surface Design

## Purpose

Define the first concrete `v0.5` contract step:

- how RTDL should expose a true 3D nearest-neighbor public surface
- how that surface should relate to the existing released 2D line
- what must be implemented before the new surface is considered online

This goal is a design-closure goal, not a fake feature-release goal.

## Why This Goal Exists

Current `v0.4.0` nearest-neighbor workloads are structurally 2D-first.

That shows up in the public surface and runtime assumptions:

- `src/rtdsl/types.py` defines `Point2DLayout` and `Points`
- CPU/reference point handling uses `Point(id, x, y)`
- native/runtime packing paths are still hard-coded around `x, y`

That is sufficient for the released line.

It is not sufficient for a paper-consistent RTNN-style 3D experiment package.

## Design Requirements

### 1. Keep the released 2D line stable

`v0.5` must not break:

- `fixed_radius_neighbors`
- `knn_rows`
- existing 2D examples
- existing 2D benchmarks and reports

### 2. Add a real 3D point surface

The public type layer should gain a first-class 3D point geometry surface,
instead of forcing 3D through ad hoc layouts.

Minimum design target:

- `Point3DLayout`
- `Points3D`
- 3D-aware normalization / record coercion paths

### 3. Keep workload naming stable unless semantics change

If the only change is dimensionality support, keep the workload family names:

- `fixed_radius_neighbors`
- `knn_rows`

If the contract changes materially, expose the new contract explicitly rather
than overloading the old name silently.

### 4. Distinguish two separate questions

`v0.5` must keep these separate:

1. dimensionality support
2. paper-consistent bounded-radius KNN semantics

Adding 3D support alone does not solve the bounded-radius KNN question.

### 5. Do not expose unsupported public promises

A 3D nearest-neighbor surface should only be called online when all of these
exist:

- public API surface
- Python/reference truth path
- CPU/oracle path
- lowering support
- backend-specific acceptance status written honestly

## Proposed Sequence

1. public type design
   - `Point3DLayout`
   - `Points3D`
   - public docs and contract text

2. reference/correctness path
   - 3D point dataclass or equivalent canonical record form
   - reference `fixed_radius_neighbors`
   - reference `knn_rows`

3. runtime/normalization path
   - input coercion
   - CPU/oracle path

4. backend bring-up
   - Embree
   - OptiX
   - Vulkan

5. experiment layer
   - first 3D benchmark and parity checks

## Non-Goals

This goal does not itself ship:

- a released 3D nearest-neighbor workload
- final bounded-radius KNN semantics
- full RTNN reproduction harnesses

It defines the contract and implementation order for the first real `v0.5`
surface step.

## Success Condition

This goal is successful if the repo has a saved, reviewed design agreement that:

- names the required 3D public surface
- preserves the released 2D line
- keeps dimensionality and paper-contract changes separate
- defines the correct implementation order for the next coding goals
