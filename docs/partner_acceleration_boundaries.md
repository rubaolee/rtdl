# Partner Acceleration Boundaries

RTDL's partner path lets Python programs pass partner-owned columns into RTDL
primitive calls. The supported partners are part of the data handoff contract;
they are not general-purpose program optimizers.

## What RTDL Accelerates

RTDL accelerates the RTDL primitive call you explicitly make.

For the current v2.0 work, the supported shape is:

1. You build columns in Python with NumPy, PyTorch, or CuPy.
2. You call an RTDL partner API for a supported primitive.
3. RTDL executes the primitive on the selected backend, such as Embree or OptiX.
4. RTDL returns a defined result contract, such as flags, counts, or witness
   columns.

Examples of valid narrow wording:

- RTDL can run a partner-owned ray/triangle any-hit primitive.
- RTDL can run selected prepared OptiX partner-device rows with caller-owned
  input and output columns.
- RTDL can reuse prepared scenes and output buffers for supported partner rows.

## What RTDL Does Not Accelerate

RTDL does not accelerate arbitrary PyTorch or CuPy programs.

If your Python code runs a neural network, tensor expression, optimizer step,
DataFrame operation, or custom PyTorch/CuPy kernel, RTDL does not rewrite or
speed up that code. RTDL only executes the RTDL primitive you call through the
RTDL API.

Blocked wording:

- RTDL accelerates arbitrary PyTorch code.
- RTDL accelerates arbitrary CuPy code.
- RTDL optimizes partner programs automatically.
- RTDL makes whole applications faster by default.
- RTDL provides broad RT-core acceleration for all partner workloads.

## Partner-Owned Columns Are Not Whole-Program Acceleration

Partner-owned columns mean the input or output arrays are owned by a partner
runtime such as PyTorch or CuPy. That can reduce copies for a supported RTDL
primitive path, but it does not mean the rest of the partner program is
accelerated by RTDL.

The public claim must name the exact primitive, backend, partner, output
contract, and evidence artifact.

## User-Owned Partner Continuations

v2.0 does not restrict users from doing normal partner work after an RTDL
primitive returns. If the partner is CuPy, users may continue with ordinary CuPy
operations, including `cupy.RawKernel`. If the partner is PyTorch, users may
continue with ordinary PyTorch tensor operations.

That user continuation belongs to the user's application unless RTDL ships,
measures, and reviews that exact continuation contract.

Allowed architecture:

```text
Python + CuPy + RTDL
  -> RTDL runs the generic RT primitive
  -> RTDL reads or writes selected CuPy-owned device columns
  -> user code continues with CuPy operations or CuPy RawKernel
```

Blocked claim:

```text
RTDL v2.0 accelerates arbitrary CuPy RawKernel programs.
```

Allowed claim:

```text
RTDL v2.0 can interoperate with CuPy-owned device arrays, so users can continue
with normal CuPy code, including RawKernel, subject to their own correctness and
performance responsibility.
```

The same boundary applies to user C/C++ continuations in source-tree Python
apps: RTDL does not forbid them, but their performance is not automatically an
RTDL speedup claim.

For the current four all-app control rows, the intended interpretation is:

- `database_analytics`: v2 users may write CuPy scans, reductions, or RawKernel
  grouping continuations, but those are not official speedup rows until reviewed.
- `graph_analytics`: v2 users may write CuPy graph continuations for BFS or
  triangle counting, but RTDL does not claim to accelerate those graph programs.
- `polygon_pair_overlap_area_rows`: v2 users may use RTDL for candidate
  discovery and CuPy or RawKernel for exact area refinement.
- `polygon_set_jaccard`: v2 users may use RTDL for candidate hits and CuPy or
  RawKernel for exact set intersection/union reduction.

## Current Release Boundary

v2.0 is a pre-release candidate, not a final release. The current evidence
supports documented Python+partner+RTDL contracts, including a streaming exact
witness-column contract that avoids full Python row-table materialization for
the segment/polygon any-hit row. Final release still waits for the
strict 3-AI consensus redline, including a fresh Claude-family review.

Before final v2.0 release, every public performance statement must stay inside
the reviewed evidence:

- exact primitive;
- exact app row when app-level wording is used;
- exact backend;
- exact partner;
- exact hardware class;
- exact transfer or zero-copy boundary;
- reviewed artifact path.

When those details are missing, use preview wording instead of performance
wording.

Do not use Copilot supplemental review as a replacement for the missing
Claude-family release review unless the release rule is explicitly changed.
