# RTDL v1.6 Release Audit Report

Status: all v1.6 release gates passed, and the `v1.6` annotated tag was
published after final 3-AI release consensus and explicit release/tag
authorization.

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
| Final release package | pass | this package, Claude/Gemini review |
| Final 3-AI release consensus | pass | Goal 1607 |
| Public front-door docs update | pass | README/docs updated to current release v1.6 |
| Explicit release/tag authorization | pass | user requested completion of v1.6 |

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

The v1.6 release is complete from the gate perspective and the `v1.6` tag has
been published. This audit does not authorize moving `v1.6`, moving `v1.5`, or
broadening the public claims listed above.
