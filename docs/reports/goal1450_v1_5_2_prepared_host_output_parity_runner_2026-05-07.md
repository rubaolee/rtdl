# Goal1450 v1.5.2 Prepared Host-Output Parity Runner

## Verdict

Added as a runner-only step. This does not satisfy the v1.5.2 prepared-buffer
reuse gate by itself because real Embree/OptiX same-contract execution evidence
still must be collected and reviewed.

## Scope

- Primitive: `COLLECT_K_BOUNDED`
- Track: Python+RTDL
- Runner: `scripts/goal1450_v1_5_2_prepared_host_output_parity.py`
- Local tests: `tests/goal1450_v1_5_2_prepared_host_output_parity_test.py`
- Acceptance cases: empty zero-capacity, exact-fit deduplicated rows,
  one-short fail-closed overflow, and zero-capacity positive overflow.

## Boundary

The runner targets the app-generic row-major i64 ABI through
`rtdl_embree_collect_k_bounded_i64` and `rtdl_optix_collect_k_bounded_i64`.
It validates prepared host-output behavior over caller-owned ctypes host
storage. It does not authorize true zero-copy wording, public speedup wording,
whole-app claims, stable primitive wording, or release action.

## Next Evidence

Run the script on a machine with built Embree and OptiX libraries, requiring
both backends, and then seek external review before moving
`embree_optix_same_contract_parity` out of the v1.5.2 gate's missing evidence.
