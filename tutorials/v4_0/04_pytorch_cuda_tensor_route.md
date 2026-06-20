# PyTorch CUDA Tensor Route

Status: current V4.0.0 source-tree tutorial.

This route uses detached contiguous PyTorch CUDA tensors. PyTorch owns the input
and output tensors. RTDL borrows the tensor device columns and writes fixed-size
output tensors.

Run:

```bash
PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_pytorch_hello.py
```

The supported tensor shape in this tutorial is narrow:

- CUDA tensors only;
- detached tensors only;
- one-dimensional contiguous columns;
- `ids` as `torch.uint32`;
- `x` and `y` as `torch.float64`;
- one CUDA device per route invocation.

The route rejects CPU tensors, grad-enabled tensors, non-contiguous sliced
views, bad dtypes, mismatched lengths, and output-contract mistakes. Those
fail-closed cases are part of the V4 evidence.

This tutorial does not claim a full PyTorch partner surface. It does not claim
autograd integration, compiler integration, broad PyTorch program acceleration,
async completion, public true-zero-copy wording, or speedup wording.
