# Retained packed-AoS protocol-binding failure

Date: 2026-09-09

## Identity and outcome

- Source commit: `5cc68659c0dc38990b57866511b2b6834613d1f3`.
- Source tree: `012da3c78bd144cb3ec620eb5ce4386e90cf8014`.
- Native SHA-256:
  `7da78b5ca703a021e331ab71d90fa4f6de2e98f3333a17ac5246d303456ef178`.
- Probe: real public RTDL path, first 5,000 rows of the registered 160M
  transition ensemble.
- Outcome: terminal failure before prepared GPU execution.
- Error:
  `GC014_PROTOCOL_CONTRACT_REJECTED@materialize.contract:`
  `CP003_PHYSICAL_BINDING_MISMATCH`.

## Cause

The packed AoS runtime changed `src/rtdsl/v4_triangle_prepared_runtime.py`, but
the compiler's independently stated expected runtime source SHA-256 in
`v4_public_builtin_triangle.py` still named the predecessor bytes. The protocol
contract correctly rejected the discrepancy.

## Resolution boundary

Commit `219170fee34955199049ac3808fd7a7c8263917c` updated the expected hash to
the reviewed runtime bytes and passed the runtime source-identity test and the
real public-path smoke. The check was not removed or relaxed. The failed
`5cc68659c` probe is diagnostic evidence only and is not pooled with the later
formal transaction.
