# Partner Acceleration Boundaries

RTDL's partner path lets Python programs pass partner-owned columns into RTDL
primitive calls. The supported partners are part of the data handoff contract;
they are not general-purpose program optimizers.

## What RTDL Accelerates

RTDL accelerates the RTDL primitive call you explicitly make.

For the current v2.3 release, the supported shape is:

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

RTDL does not restrict users from doing normal partner work after an RTDL
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
RTDL accelerates arbitrary CuPy RawKernel programs.
```

Allowed claim:

```text
RTDL v2.3 can interoperate with CuPy-owned device arrays, so users can continue
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

v2.3 is the current source-tree Python+partner+RTDL release. The evidence
supports documented Python+partner+RTDL contracts and separates promoted
benchmark apps from learner/example apps. The release passed the strict 3-AI
consensus redline with Codex, Claude, and Gemini.

Every public performance statement must stay inside the reviewed evidence:

- exact primitive;
- exact app row when app-level wording is used;
- exact backend;
- exact partner;
- exact hardware class;
- exact transfer or zero-copy boundary;
- reviewed artifact path.

When those details are missing, use compatibility or preview wording instead
of performance wording.

Copilot supplemental review may be useful engineering signal, but it does not
replace Claude or Gemini under the strict 3-AI consensus rule.

## v2.4/v2.5 Partner Direction

The next partner direction is performance-preserving ease of use. The goal is
to make RT-core programming substantially easier without replacing the current
10 promoted benchmark apps with slower convenience paths.

For the detailed roadmap, see
`docs/reports/goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md`.

The short boundary is:

- v2.4 should stabilize typed buffers, prepared sessions, segmented/chunked row
  streaming, and generic partner continuation contracts.
- v2.5 should add a Triton-first partner path, with Numba treated as secondary
  or exploratory.
- Triton or Numba should own preparation, continuation, reduction, compaction,
  and finalization around RTDL primitives; they must not replace OptiX RT-core
  traversal for RT-core claims.
- A friendlier partner path is not a promoted performance path if it
  significantly regresses the current same-contract OptiX-vs-Embree benchmark
  evidence.

The first implemented v2.4 slice is the RTDL-specific handoff protocol in
`src/rtdsl/partner_protocol.py`; see
`docs/reports/goal2658_v2_4_partner_protocol_foundation_2026-05-27.md`.
The next metadata-only integration slice applies that protocol to RayDB,
bounded witness collection, and RT-Graph-style triangle counting; see
`docs/reports/goal2659_v2_4_benchmark_protocol_integration_2026-05-27.md`.
The follow-up phase-timing slice adds machine-readable v2.4 timing validation
for the same prepared paths; see
`docs/reports/goal2660_v2_4_phase_timing_metadata_2026-05-27.md`.
