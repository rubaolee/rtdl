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

## Current Release Boundary

Before v2.0 release, every public performance statement must stay inside the
reviewed evidence:

- exact primitive;
- exact app row when app-level wording is used;
- exact backend;
- exact partner;
- exact hardware class;
- exact transfer or zero-copy boundary;
- reviewed artifact path.

When those details are missing, use preview wording instead of performance
wording.
