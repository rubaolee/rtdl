# Gemini Review: Goal1578 Derived Carry Alias Promotion Readiness

## Verdict

`RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` is the strongest candidate for OptiX `COLLECT_K_BOUNDED` production promotion, but it must remain diagnostic until validation is completed on at least one additional NVIDIA architecture.

## Missing Evidence

- Hardware diversity is the primary blocker.
- Validation is required on a second NVIDIA architecture such as Ampere, Hopper, Blackwell, or another non-Ada RTX device with enough shared memory for the tiled row-width-2 path.
- The local Linux GTX 1070 is insufficient for accepted performance evidence.
- Current evidence does not authorize broad RTX/GPU acceleration wording, true zero-copy wording, release action, or promotion of `COLLECT_K_BOUNDED` from experimental to stable.

## Risk Assessment

- Correctness and parity are clean on the measured RTX 4000 Ada pod.
- The alias path preserves the derived descriptor fast path.
- The topology guard has been validated to block unsafe aliases while allowing safe aliases.
- Physical row-payload copies are now accounted for separately.
- Pointer descriptor alternatives were measured and rejected.
- The bounded even/odd sweep covered bitonic, no-carry, blocked-carry, mixed blocked/safe carry, and safe-carry merge cases.

## Promotion Criteria Feedback

Promotion becomes reasonable if the second architecture shows:

- accepted Goal1506-style evidence,
- passing parity across all sweep cases,
- profile topology matching expectations,
- no correctness failure in blocked aliases,
- no material regression in no-carry scenarios,
- improvements or neutrality in carry scenarios after targeted rerun if necessary.

## Claim Boundary Feedback

The report is correctly framed as a promotion-readiness artifact only. It does not authorize public speedup wording, true zero-copy wording, stable primitive promotion, whole-application claims, or release action.
