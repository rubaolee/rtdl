# Goal1952 - Partner RawKernel And User Continuation Boundary

Status: boundary-documented-not-speedup-evidence

Date: 2026-05-13

## Question

If CuPy is an RTDL v2.0 partner, does v2.0 allow users to continue with normal
CuPy work such as `cupy.RawKernel`?

Yes. v2.0 allows it.

The important distinction is ownership of the claim, not permission to run the
code.

## Two Layers

```text
Layer 1: RTDL partner contract
  RTDL runs a generic primitive and reads/writes selected partner-owned columns.

Layer 2: User partner program
  The user's Python program continues with normal partner code, such as CuPy
  ufuncs, reductions, scans, or RawKernel.
```

v2.0 does not try to limit Layer 2. A user can use CuPy normally, including
`RawKernel`, after RTDL produces or consumes CuPy-owned device arrays.

## Claim Boundary

Allowed:

```text
RTDL v2.0 can interoperate with CuPy-owned device arrays, so users can continue
with normal CuPy code, including RawKernel.
```

Blocked:

```text
RTDL v2.0 accelerates arbitrary CuPy RawKernel programs.
```

Why: a `RawKernel` is user-owned GPU program text. RTDL did not synthesize,
verify, optimize, or semantically own that kernel. If RTDL wants to claim a
specific RawKernel continuation as official v2.0 evidence, that exact
continuation needs its own implementation, correctness check, performance
artifact, and external review.

## v1.8 Analogy

In v1.8, the app shape is:

```text
Python + RTDL
  -> RTDL runs the generic RT part
  -> Python owns the non-RT continuation
```

The Python continuation may call user C/C++ code. RTDL does not forbid this.
Goal1948 demonstrates that pattern with a Hausdorff example:

```text
RTDL generic k=1 nearest-neighbor rows
  -> learner-owned C++ max-distance reduction
  -> Python result assembly and oracle check
```

That C++ continuation proves interoperability, not official RTDL v2.0 partner
speedup.

## v2.0 CuPy Analogy

In v2.0, the analogous app shape is:

```text
Python + CuPy + RTDL
  -> RTDL runs the generic RT part
  -> CuPy owns GPU arrays around the RTDL primitive
  -> user code may continue with CuPy operations or RawKernel
```

This is normal and allowed v2.0 usage. It becomes official RTDL performance
evidence only when the exact continuation is reviewed as part of a measured
contract.

## Four Current Control Apps

The four all-app control rows are not controls because v2.0 forbids partner
continuations. They are controls because the specific continuations have not yet
been implemented, measured, and reviewed as official v2.0 partner evidence.

| Control app | Allowed user continuation | Why still control |
| --- | --- | --- |
| `database_analytics` | CuPy scans, reductions, segmented/grouped reductions, or RawKernel grouping code | No reviewed app-agnostic partner columnar scan/grouped-reduction contract yet. |
| `graph_analytics` | CuPy arrays plus RawKernel or library code for BFS, visibility post-processing, or triangle counting | Graph algorithms are outside the current reviewed RTDL partner speedup contract. |
| `polygon_pair_overlap_area_rows` | RTDL candidate discovery followed by CuPy or RawKernel exact area refinement | Candidate discovery is RT-shaped; exact area refinement is not yet a reviewed partner continuation. |
| `polygon_set_jaccard` | RTDL candidate hits followed by CuPy or RawKernel set union/intersection reduction | Exact set reduction dominates and lacks a reviewed partner continuation contract. |

## User Mental Model

The clean way to teach this is:

```text
RTDL owns the generic RT primitive.
The partner owns the arrays.
The user owns the rest of the program unless RTDL explicitly ships and reviews
that continuation as part of the release evidence.
```

This keeps v2.0 general-purpose without pretending that RTDL accelerates every
possible program written in a partner framework.

## Release Boundary

This document does not authorize any new v2.0 speedup row. It clarifies allowed
usage and claim ownership:

- CuPy `RawKernel` is allowed user-side partner code.
- User C/C++ continuation is allowed user-side Python code.
- Neither automatically counts as official RTDL speedup evidence.
- A specific continuation may become official evidence only after exact
  implementation, measurement, and external review.
