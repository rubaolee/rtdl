# Handoff: Goal1804 v2.0 Partner OptiX Pod Packet Review

Please perform an independent Gemini read-only review of the Goal1804 v2.0
partner OptiX pod packet.

## Context

RTDL v1.8 is published. The active roadmap target is v2.0:
Python + partner + RTDL. The standing partner consensus is:

```text
Protocol first. PyTorch reference first. CuPy conformance alongside it.
Engine absolutely app-agnostic throughout.
```

Goal1804 does not run a pod. It prepares the concentrated pod packet for later
RTX-class OptiX validation of the first public partner any-hit dispatch.

## Files To Inspect

- `scripts/goal1804_v2_partner_optix_pod_runner.sh`
- `tests/goal1804_v2_partner_optix_pod_packet_test.py`
- `docs/reports/goal1804_v2_partner_optix_pod_packet_2026-05-12.md`
- `docs/release_reports/v1_8_v2_0_python_partner_rtdl_gate.md`
- supporting context if needed:
  - `examples/rtdl_partner_anyhit.py`
  - `docs/tutorials/partner_anyhit.md`
  - `src/rtdsl/partner.py`
  - `tests/goal1799_partner_anyhit_public_dispatch_test.py`
  - `tests/goal1787_optix_partner_anyhit_host_stage_test.py`

## Review Questions

1. Does the runner capture enough environment and build/test evidence for the
   next RTX-class pod run?
2. Does it validate NumPy CPU, PyTorch CUDA, and CuPy CUDA through
   `backend=optix` using the public partner example?
3. Does it preserve the claim boundary: no true zero-copy claim, no direct
   device-pointer handoff claim, no RT-core speedup claim, and no v2.0 release
   readiness claim?
4. Is the static test aligned with the runner and report?
5. Is the release gate link appropriately narrow and non-overclaiming?

## Expected Output

Write the review to:

```text
docs/reviews/goal1805_gemini_review_goal1804_v2_partner_optix_pod_packet_2026-05-12.md
```

Use one of the allowed verdict terms:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

For this pre-pod packet, prefer `accept-with-boundary` if the packet is sound
but still depends on future RTX-class pod execution.

Do not modify source, runner, tests, reports, or release gates other than the
single review file above.
