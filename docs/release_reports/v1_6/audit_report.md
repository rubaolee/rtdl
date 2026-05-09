# RTDL v1.6 Release Audit Report

Status: final release-candidate audit. Do not publish or tag until final 3-AI
release consensus is accepted and explicit release/tag authorization is
confirmed.

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Historical Python+RTDL readiness boundary | pass | Goal 1599, 3-AI consensus |
| Machine-readable readiness gate | pass | Goal 1600, 3-AI consensus |
| Formal release-surface proposal | pass | Goal 1601, 3-AI consensus |
| Public docs overclaim audit | pass | Goal 1602, 3-AI consensus |
| Stable native-path app-leakage audit | pass with bounded claim | Goal 1603, 3-AI consensus |
| Blocked-claim regression | pass | Goal 1604, 3-AI consensus |
| Windows source-tree validation | pass | Goal 1605, 38-test slice |
| Linux source-tree validation | pass | Goal 1605, 38-test slice |
| Real NVIDIA OptiX validation | pass | Goal 1605, 33-test GTX 1070 slice |
| Final release package | pending final review | this package |
| Final 3-AI release consensus | pending | required before publish/tag |
| Explicit release/tag authorization | pending | required before publish/tag |

## Release Boundary

v1.6 is the first Python+RTDL architecture milestone. It closes the first
architecture track by making the Python+RTDL contract public and explicit:
Python controls app logic, RTDL owns the supported RT-shaped primitive contract
and bridge, and Embree/OptiX execute the validated native primitive subpaths.

v1.6 is not a universal compute engine, package-install release, whole-app
speedup release, true zero-copy release, or partner tensor-handoff release.

The stable public surface is app-generic at the primitive-contract level, but
native internals are not fully app-agnostic. App-shaped compatibility/proof
entry points remain and are excluded from the stable public claim.

## Validation Summary

Windows source-tree validation:

```text
Ran 38 tests
OK
```

Linux source-tree validation:

```text
Ran 38 tests
OK
```

Linux NVIDIA OptiX validation:

```text
NVIDIA GeForce GTX 1070, 580.126.09
Ran 33 tests
OK
```

Validated commit:

```text
ae92aa8eabc969da856ea730c7b82e19345ca3a3
```

## Allowed

- Publish v1.6 as the first Python+RTDL architecture milestone after final
  consensus and release/tag authorization.
- Claim source-tree Python+RTDL usage.
- Claim Embree and OptiX as active closure backends for the scoped stable
  primitive surface.
- Claim the stable primitive boundary:
  `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
  `REDUCE_INT(COUNT|SUM)`.
- Claim Windows/Linux validation for the recorded source-tree slices.
- Claim real NVIDIA OptiX runtime validation for the recorded scoped slice.

## Not Allowed

- Treating this audit document as release/tag authorization by itself.
- Package-install support.
- Arbitrary Python optimization.
- Whole-app speedup.
- Broad NVIDIA RTX/GPU acceleration.
- True zero-copy.
- Partner tensor handoff.
- Stable `COLLECT_K_BOUNDED` promotion.
- Claims that native internals are fully app-agnostic.
- Treating Vulkan, HIPRT, or Apple RT as active v1.6 implementation targets.

## Result

The final v1.6 release package is ready for final external review and final
3-AI release consensus.

Do not publish or tag `v1.6` until final consensus is accepted and explicit
release/tag authorization is confirmed.
