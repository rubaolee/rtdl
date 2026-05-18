# OptiX Partner Column Any-Hit

This tutorial explains the current v2.0 OptiX partner-column idea. It is not a
broad GPU-speedup promise.

Read [Python Partner Any-Hit](partner_anyhit.md) first if you have not already
seen the partner descriptor shape.

## What This Path Demonstrates

The supported shape is:

```text
CuPy or PyTorch owns input columns
  -> RTDL runs a prepared OptiX any-hit primitive
  -> RTDL writes documented output columns
  -> Python or the partner framework continues from those columns
```

The important lesson is column ownership. A user can keep data in a partner
runtime and avoid turning every result into Python dictionaries when a compact
or streaming output contract is available.

## Minimal Mental Model

| Part | Owner |
| --- | --- |
| app data and policy | Python |
| input/output tensors | PyTorch or CuPy |
| RT-shaped primitive | RTDL |
| native traversal | OptiX |
| post-processing | user Python or partner code |

## Claim Boundary

Allowed:

- prepared OptiX partner-column primitive under documented contracts;
- partner-owned input and output columns for the supported path;
- continuation with normal PyTorch or CuPy code after RTDL returns.

Not allowed:

- arbitrary PyTorch or CuPy acceleration;
- broad RT-core acceleration;
- package-install support;
- claims that every app phase is faster.

For the current release status, read
[v2.0 Release Package](../release_reports/v2_0/README.md).

## Practical Starting Point

Start with the portable partner tutorial first:

```bash
PYTHONPATH=src:. python examples/rtdl_partner_anyhit.py --partner numpy --backend embree
```

Move to OptiX only on a configured NVIDIA host with the OptiX backend built.
When measuring performance, record the exact backend, partner, hardware,
command, output contract, and artifact path.
