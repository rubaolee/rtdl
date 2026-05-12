# Goal1781: Real-Framework Partner Availability Gate

Status: `accept-with-boundary`

Date: 2026-05-12

## Context

Goal1777 froze the v2.0 Python+partner+RTDL protocol baseline with 3-AI
consensus. The next v2.0 step is to move from fake-framework contract tests to
real PyTorch and CuPy behavior.

The local Linux host without RT cores is a useful development platform for this
slice. It can validate Python framework behavior, descriptors, DLPack metadata,
CPU PyTorch, and skip boundaries. It cannot prove OptiX RT-core acceleration,
CUDA device-resident handoff, or final v2.0 hardware readiness.

## Test Added

New test:

```text
tests/goal1781_real_framework_partner_availability_test.py
```

The test is portable across Windows, local Linux, and pod environments. It uses
actual frameworks when installed and records explicit skip reasons otherwise.

Coverage:

- PyTorch CPU tensor export through `rt.partner.auto()`;
- PyTorch CPU output allocation through `rt.partner.use("torch").empty(...)`;
- grad-enabled PyTorch tensor rejection;
- PyTorch CUDA descriptor export when CUDA is available;
- CuPy CUDA tensor export and output allocation when CuPy and CUDA are
  available;
- CuPy CPU output rejection when CuPy is installed.

## Local Windows Evidence

Local framework probe:

```text
torch: no
cupy: no
numpy: yes
```

Local validation:

```text
PYTHONPATH=src py -3 -m unittest \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test
```

Result:

```text
18 tests ran.
13 passed.
5 skipped.
```

Skip reason:

```text
PyTorch is not installed in this dev environment.
CuPy is not installed in this dev environment.
```

The local Python launcher also prints:

```text
Could not find platform independent libraries <prefix>
```

That launcher warning did not affect the test result.

## Local Linux Attempt

Attempted local Linux access:

```text
ssh -o BatchMode=yes -o ConnectTimeout=5 root@192.168.1.20 ...
ssh -o BatchMode=yes -o ConnectTimeout=5 -i id_ed25519_rtdl_codex root@192.168.1.20 ...
```

Both attempts returned:

```text
root@192.168.1.20: Permission denied (publickey,password).
```

This is an environment access blocker only. It does not block the code/test
slice, and it does not require a pod yet.

## Dev Platform Use

Once local Linux access is available, run:

```text
PYTHONPATH=src python3 -m unittest \
  tests.goal1781_real_framework_partner_availability_test \
  tests.goal1777_v2_0_partner_protocol_baseline_test \
  tests.goal1675_partner_protocol_substrate_test
```

Interpretation:

- PyTorch CPU installed: PyTorch CPU export/allocation and grad rejection should
  pass.
- PyTorch CUDA absent: CUDA subtest should skip with a clear no-CUDA reason.
- CuPy absent: CuPy tests should skip with a clear no-CuPy reason.
- CuPy installed but no CUDA: CuPy tests should skip with a clear device-query
  or no-device reason.

## Non-Claims

Goal1781 does not claim:

- true zero-copy support;
- CUDA device-resident handoff;
- OptiX partner descriptor execution;
- RT-core acceleration;
- v2.0 release readiness.

## Verdict

`accept-with-boundary`: the real-framework availability gate exists and is
portable. The current Windows machine has no PyTorch/CuPy evidence, and local
Linux access is blocked by SSH authentication. No pod is needed until we are
ready to collect CUDA/CuPy/OptiX hardware evidence.
