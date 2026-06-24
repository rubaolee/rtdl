# Goal1785: Linux PyTorch and CuPy Partner Validation

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goal1777 froze the v2.0 partner protocol baseline. Goal1781 added a portable
real-framework availability gate. Goal1783 added the NumPy CPU partner adapter.

Goal1785 runs the real PyTorch and CuPy portions of that gate on the local Linux
validation host.

## Host

```text
host: 192.168.1.20
user: lestat
checkout: /home/lestat/work/rtdl_v2_partner_check
git commit: 57848676a2618b2fd6e8d7f525741f4c83696d96
gpu: NVIDIA GeForce GTX 1070
driver: 580.126.09
nvcc: CUDA 12.0
```

The existing Linux checkouts were dirty, so a fresh checkout was created at:

```text
/home/lestat/work/rtdl_v2_partner_check
```

## Environment Setup

The host did not have `python3.12-venv`, and `lestat` did not have
passwordless sudo. System Python is externally managed by Debian/Ubuntu PEP 668.

To avoid mutating system Python, the frameworks were installed into a checkout
local target directory:

```text
cd /home/lestat/work/rtdl_v2_partner_check
mkdir -p .partner_site
python3 -m pip install --target .partner_site --index-url https://download.pytorch.org/whl/cu121 torch
python3 -m pip install --target .partner_site cupy-cuda12x
```

Installed local package footprint:

```text
.partner_site: 5.3G
```

## Framework Probe

Run command:

```text
PYTHONPATH=.partner_site:src:. python3 -
```

Probe result:

```text
torch 2.5.1+cu121 cuda_available True torch_cuda 12.1
torch cuda tensor cuda:0 128244361723904 [0.0, 1.0, 2.0, 3.0]
cupy 14.0.1 numpy 2.4.4
cupy device count 1
cupy tensor <CUDA Device 0> 128244365918208 [0.0, 1.0, 2.0, 3.0]
```

## RTDL Partner Validation

Run command:

```text
cd /home/lestat/work/rtdl_v2_partner_check
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1783_numpy_cpu_partner_adapter_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test
```

Result:

```text
22 tests ran.
22 passed.
0 skipped.
```

This validates:

- real PyTorch CPU tensor export;
- real PyTorch CPU output allocation;
- real PyTorch grad-enabled tensor rejection;
- real PyTorch CUDA descriptor export;
- real CuPy CUDA tensor export;
- real CuPy CUDA output allocation;
- CuPy CPU output rejection;
- real NumPy CPU partner descriptor behavior;
- non-contiguous NumPy host stride preservation.

## Boundary

This is real PyTorch/CuPy/NumPy framework evidence on a CUDA-capable Linux host.
It is not final v2.0 hardware readiness.

Non-claims:

- no OptiX partner-descriptor execution path has been wired yet;
- no true zero-copy claim is made;
- no phase timing separates device-resident handoff, fallback copy, and host
  staging yet;
- no RT-core acceleration claim is made from this test;
- no v2.0 release readiness claim is made.

The GTX 1070 is useful for framework/CUDA smoke validation. It is not the final
NVIDIA RT-core performance pod for v2.0 release evidence.

## Next Step

The next v2.0 implementation slice should wire one narrow app-agnostic OptiX
primitive path, preferably `ANY_HIT` or `COUNT_HITS`, through partner
descriptors. That next slice will need hardware validation and phase-timing
artifacts.

## Verdict

`accept-with-boundary`: the v2.0 partner framework gate now has real Linux
PyTorch CUDA, CuPy CUDA, and NumPy CPU evidence. v2.0 remains blocked until the
first OptiX partner-descriptor execution path and timing evidence exist.
