# Goal1802: Partner Any-Hit Learner Docs And Example

Status: `accept-with-boundary`

Date: 2026-05-12

## Scope

Goal1802 adds the learner-facing documentation and example for the first v2.0
Python+partner+RTDL path.

New files:

- `examples/rtdl_partner_anyhit.py`
- `docs/tutorials/partner_anyhit.md`
- `tests/goal1802_partner_anyhit_docs_example_test.py`

Updated indexes:

- `docs/README.md`
- `docs/tutorials/README.md`
- `docs/app_example_quickstart.md`
- `examples/README.md`

## What The Example Teaches

The example shows the first v2.0 partner bridge:

```text
NumPy / PyTorch CUDA / CuPy CUDA columns
  -> RTDL partner descriptor
  -> explicit host staging
  -> Embree or OptiX 2-D ray/triangle ANY_HIT count
```

Default command:

```text
PYTHONPATH=src:. python examples/rtdl_partner_anyhit.py --partner numpy --backend embree
```

Embree is the default because it is the no-pod CPU RT development path.

## Claim Boundary

The tutorial and example explicitly preserve the current v2.0 boundaries:

- partner logic stays in Python adapter code;
- native engines remain app-agnostic;
- first-wave partner execution is host-stage;
- true zero-copy is not authorized;
- RT-core speedup wording is not authorized;
- timing fields are not benchmark evidence.

## Validation

Windows command:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal1802_partner_anyhit_docs_example_test \
  tests.goal1799_partner_anyhit_public_dispatch_test \
  tests.goal1795_embree_partner_anyhit_host_stage_test
```

Result:

```text
11 tests ran.
8 passed.
3 skipped.
py_compile passed for the example and test.
```

Linux command:

```text
PYTHONPATH=.partner_site:src:. python3 -m unittest \
  tests.goal1802_partner_anyhit_docs_example_test \
  tests.goal1799_partner_anyhit_public_dispatch_test \
  tests.goal1795_embree_partner_anyhit_host_stage_test
```

Result on `192.168.1.20`:

```text
11 tests ran.
11 passed.
0 skipped.
```

The Linux host also ran the example through Embree for all three first-wave
partner inputs:

```text
PYTHONPATH=.partner_site:src:. python3 examples/rtdl_partner_anyhit.py --partner numpy --backend embree
PYTHONPATH=.partner_site:src:. python3 examples/rtdl_partner_anyhit.py --partner torch-cuda --backend embree
PYTHONPATH=.partner_site:src:. python3 examples/rtdl_partner_anyhit.py --partner cupy-cuda --backend embree
```

All three runs returned `hit_count = 1`, `transfer_mode = "host_stage"`,
`true_zero_copy_authorized = false`, and
`rt_core_speedup_claim_authorized = false`.

## Independent Review

- [Goal1803 Gemini review](../reviews/goal1803_gemini_review_goal1802_partner_anyhit_learner_docs_2026-05-12.md): `accept-with-boundary`

## Verdict

`accept-with-boundary`: the first v2.0 partner path now has a runnable learner
example and tutorial, but v2.0 release readiness remains blocked on the
non-Embree gates described in the release gate.
