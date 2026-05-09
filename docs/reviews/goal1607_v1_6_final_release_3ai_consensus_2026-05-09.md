# 3-AI Consensus: RTDL v1.6 Final Release

## Verdict

Accepted for final public-release completion after the public front-door docs
are updated to point at the v1.6 package and the final tag target commit is
clean.

Codex, Claude, and Gemini agree that the v1.6 release package is honest,
properly scoped, and consistent with Goals 1599-1606.

Reviewed release-package commit:

```text
6477a55d Add v1.6 release package
```

## Consensus Release Statement

RTDL v1.6 is the first Python+RTDL architecture milestone. Python remains the
app/control layer, while RTDL owns the supported RT-shaped primitive contract
and bridge to native Embree/OptiX execution. The stable public surface is
limited to reviewed primitive subpaths: `ANY_HIT`, `COUNT_HITS`,
`REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.

RTDL does not optimize arbitrary Python code or whole applications; performance
claims remain scoped to exact reviewed primitive subpaths.

## Accepted Evidence

The consensus accepts these closure artifacts:

- Goal 1599: v1.6 historical Python+RTDL readiness boundary.
- Goal 1600: machine-readable v1.6 readiness gate.
- Goal 1601: release-surface proposal.
- Goal 1602: public-docs overclaim audit.
- Goal 1603: stable native-path app-leakage audit.
- Goal 1604: blocked-claim regression gate.
- Goal 1605: Windows/Linux source-tree and real NVIDIA OptiX validation.
- Goal 1606: v1.6 release package.

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

## Claim Boundary

Allowed public claims:

- v1.6 closes the first Python+RTDL architecture track.
- Python remains the app/control layer.
- RTDL owns the supported RT-shaped primitive contract and bridge.
- Embree and OptiX are the active v1.6 closure backends.
- The stable primitive boundary is `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- Windows and Linux source-tree validation passed for the scoped release slice.
- Real NVIDIA OptiX runtime validation passed for the scoped primitive/reduction
  paths.

Blocked public claims:

- package-install support;
- arbitrary user-Python optimization;
- whole-application speedup;
- broad NVIDIA RTX/GPU acceleration;
- every `--backend optix` run being a NVIDIA RT-core speedup;
- true zero-copy support;
- partner tensor handoff support;
- stable `COLLECT_K_BOUNDED` promotion;
- fully app-agnostic native internals;
- active Vulkan, HIPRT, or Apple RT implementation targets.

## Review Notes

Claude found one release-package provenance issue: the tag preparation note
initially treated the Goal 1605 validation commit as the candidate tag commit
even though the release package itself was not yet committed. This was fixed by
separating the Goal 1605 validation commit from the final tag target commit.

Gemini found no package blockers and accepted the package as honest and
accurate.

## Final Release Steps

Before creating the `v1.6` tag:

- update public front-door docs so the current release is v1.6;
- rerun the final v1.6 package/gate test slice;
- ensure the worktree is clean except known unrelated local artifacts;
- create the annotated `v1.6` tag on the final clean release commit;
- push `main` and the `v1.6` tag.

## Recommendation

Proceed with the public-doc update and final tag action for `v1.6` on the final
clean release commit.
