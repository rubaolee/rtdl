# Partner Acceleration Boundaries

RTDL's partner path lets Python programs pass partner-owned columns into RTDL
primitive calls. The supported partners are part of the data handoff contract;
they are not general-purpose program optimizers.

## What RTDL Accelerates

RTDL accelerates the RTDL primitive call you explicitly make.

For the current v2.x source-tree surface, the supported shape is:

1. You build columns in Python with NumPy, PyTorch, CuPy, or Numba-compatible
   arrays.
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

RTDL does not accelerate arbitrary PyTorch, CuPy, or Numba programs.

If your Python code runs a neural network, tensor expression, optimizer step,
DataFrame operation, custom CuPy kernel, or custom Numba kernel, RTDL does not
rewrite or speed up that code. RTDL only executes the RTDL primitive you call
through the RTDL API.

Blocked wording:

- RTDL accelerates arbitrary PyTorch code.
- RTDL accelerates arbitrary CuPy code.
- RTDL accelerates arbitrary Numba code.
- RTDL optimizes partner programs automatically.
- RTDL makes whole applications faster by default.
- RTDL provides broad RT-core acceleration for all partner workloads.

## Partner-Owned Columns Are Not Whole-Program Acceleration

Partner-owned columns mean the input or output arrays are owned by a partner
runtime such as PyTorch, CuPy, or Numba-compatible CUDA arrays. That can reduce
copies for a supported RTDL primitive path, but it does not mean the rest of the
partner program is accelerated by RTDL.

The public claim must name the exact primitive, backend, partner, output
contract, and evidence artifact.

## User-Owned Partner Continuations

RTDL does not restrict users from doing normal partner work after an RTDL
primitive returns. If the partner is CuPy, users may continue with ordinary CuPy
operations, including `cupy.RawKernel`. If the partner is Numba, users may
continue with their own Numba CUDA kernels. If the partner is PyTorch, users may
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
RTDL v2.x can interoperate with CuPy-owned device arrays, so users can continue
with normal CuPy code, including RawKernel, subject to their own correctness and
performance responsibility.
```

The same boundary applies to user C/C++ continuations in source-tree Python
apps: RTDL does not forbid them, but their performance is not automatically an
RTDL speedup claim.

For app continuations, the intended interpretation is:

- use RTDL primitives for the traversal-heavy, app-agnostic contract;
- use CuPy for mature CUDA-array scans, masks, reductions, and RawKernel paths;
- use Numba for measured custom CUDA-style continuations such as selected
  compact masks and grouped reductions;
- keep app policy, labels, graph iteration, GIS interpretation, SQL-like
  semantics, and final reports in Python or user partner code unless RTDL has
  shipped a reviewed generic primitive for that exact contract.

## Current Release And Pre-Release Boundary

v2.3 is the current released source-tree Python+partner+RTDL evidence package.
The active v2.6 lane is internal pre-release work for clearer user-chosen
partner guidance and selected Numba custom-continuation support. v2.6 is not a
release tag yet and does not authorize package-install wording, broad speedup
wording, automatic partner selection, or a general true-zero-copy product claim.

Every public performance statement must stay inside the reviewed evidence:

- exact primitive;
- exact app row when app-level wording is used;
- exact backend;
- exact partner;
- exact hardware class;
- exact transfer or residency boundary;
- reviewed artifact path.

When those details are missing, use compatibility or preview wording instead
of performance wording.

Copilot supplemental review may be useful engineering signal, but it does not
replace Claude or Gemini under the strict 3-AI consensus rule.

## v2.6 Partner Choice Rule

The current pre-release rule is intentionally simple:

- Use a fused generic native RTDL primitive when it exactly expresses the work.
- Use partner continuation only for unfused work or explicit app choice.
- Users choose supported partners explicitly. RTDL guidance may recommend a
  partner only when same-contract evidence supports that recommendation.
- CuPy is the mature CUDA-array and library-continuation partner.
- Numba is the v2.6 custom CUDA-style continuation lane for selected measured
  contracts such as compact masks and grouped reductions.
- PyTorch remains useful for tensor interop and reference paths where measured.
- Triton remains paused for recommended paths until same-contract timing proves
  it should return.

The benchmark reference implementations document recommendations, not hidden
dispatch defaults. If a user chooses a different partner, that choice is allowed
application code; it becomes an RTDL-supported recommendation only after the
same contract is measured, reviewed, and recorded.

Current guidance lives in:

- [Choosing A Partner For Custom Logic](learn/partner_choice_for_custom_logic.md)
- [Benchmark Partner Reference Matrix](learn/benchmark_partner_reference_matrix.md)
- `docs/reports/goal3050_partner_choice_for_custom_logic_docs_and_benchmark_matrix_2026-06-02.md`
- `docs/reports/goal3052_partner_choice_pod_refresh_2026-06-02.md`
- `docs/reports/goal3054_v2_6_machine_readable_partner_choice_guidance_2026-06-02.md`

Historical v2.4/v2.5 partner-continuation reports remain in `docs/reports/`
for reviewers, including
`docs/reports/goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md`,
`docs/reports/goal2662_v2_5_partner_continuation_contract_2026-05-27.md`, and
`docs/reports/goal2981_v2_5_closeout_positioning_and_external_review_packet_2026-06-01.md`.
Those reports explain how the project reached the current v2.6 rule; they do
not override this learner-facing boundary.
