# Goal 1435 External Review Request

Please review the current uncommitted Goal1435 patch in this repository.

## Scope

Goal1435 hardens the v1.5.1 `COLLECT_K_BOUNDED` readiness evidence registry. The readiness gate already has six required gates, but the evidence registry previously named only three evidence entries because some files served more than one gate. This patch requires the registry to name every required gate explicitly and in order.

## Files To Review

- `src/rtdsl/v1_5_1_collect_k_bounded.py`
- `tests/goal1418_v1_5_1_collect_k_readiness_gate_test.py`
- `tests/goal1435_v1_5_1_collect_k_readiness_evidence_registry_test.py`
- `docs/reports/goal1435_v1_5_1_collect_k_readiness_evidence_registry_hardening_2026-05-07.md`

## Local Validation

Windows focused slice:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1435_v1_5_1_collect_k_readiness_evidence_registry_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1434_v1_5_1_full_pod_regression_test
Ran 21 tests in 0.107s
OK
```

Linux GPU pod focused slice:

```text
cd /workspace/rtdl
source /tmp/rtdl_goal1429_pod_env.sh
PYTHONPATH=src:. RTDL_OPTIX_LIB=/workspace/rtdl/build/librtdl_optix.so python3 -m unittest tests.goal1435_v1_5_1_collect_k_readiness_evidence_registry_test tests.goal1418_v1_5_1_collect_k_readiness_gate_test tests.goal1419_v1_5_1_collect_k_release_surface_proposal_test tests.goal1420_v1_5_1_collect_k_release_surface_gate_test tests.goal1434_v1_5_1_full_pod_regression_test
Ran 21 tests in 0.224s
OK
```

`git diff --check` passed with only Windows LF-to-CRLF warnings.

## Review Questions

1. Does this patch correctly require explicit evidence coverage for all six readiness gates?
2. Does it avoid changing the `COLLECT_K_BOUNDED` claim boundary or accidentally authorizing stable promotion?
3. Are there any blockers that should prevent committing this hardening patch?

Please answer with `ACCEPT`, `ACCEPT WITH NOTES`, or `REJECT`, and list any precise blockers if rejected.
