# Prepared Host-Output Buffer Candidate Surface

The v1.5.2 candidate surface records prepared host-output evidence for
`COLLECT_K_BOUNDED` in the Python+RTDL track.

Classification: documented experimental evidence candidate.

Scope:

- primitive: `COLLECT_K_BOUNDED`
- result layout: row-major dense candidate-id rows
- host storage: caller-owned ctypes int64 output buffer
- active backend evidence: Embree and OptiX
- overflow policy: fail closed before partial result materialization

Evidence basis:

- prepared collect-buffer metadata contract
- native generic i64 ABI pointer shape
- Python wrapper caller-owned host output pointer plumbing
- Python-wrapper host buffer reuse measurement
- fail-closed prepared host-output overflow validation
- same-contract Embree and OptiX parity on an RTX 2000 Ada pod
- Claude and Gemini external claim review

Current gate status: `evidence_complete_claims_blocked`.

Forbidden claims:

- prepared_buffer_reuse_proven remains False
- not stable primitive promotion
- no public speedup wording
- no zero-copy wording
- no whole-app claims
- no release tag action
- pending external release-surface review

This surface does not claim true zero-copy, device-resident output, broad
row-returning app acceleration, or whole-app speedup. It only records that the
prepared host-output evidence gate is complete while claim-specific gates remain
closed.
