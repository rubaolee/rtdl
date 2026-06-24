# RTDL Quick Tutorial

Status: paused for V3 rebuild on 2026-06-20.

This tutorial is intentionally paused. The previous version taught useful RTDL
ideas, but it linked to old tutorial tracks and support wording that are no
longer current.

## Safe First Run

From the repository root:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_hello_world.py
```

Expected output:

```text
hello, world
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\current\getting_started\rtdl_hello_world.py
```

This is a development sanity command only. It does not certify V3, backend
support, or performance.

## What The Rebuilt Tutorial Must Teach

The rebuilt V3 quick tutorial must let a user learn RTDL without reading
history:

- what problem RTDL solves over the V2.x line;
- the stable kernel shape;
- how to choose a supported backend;
- how to interpret prepared execution and measurement;
- which exact rows are M7-qualified, blocked, or still internal;
- where performance evidence lives;
- what RTDL does not claim.

Current authority:

- [V3 Rebuild Control](rebuild/v3/README.md)
- [Current Claim Boundaries](learn/current_claim_boundaries.md)
- [Tutorials Status](../tutorials/README.md)
