# Goal 1601: v1.6 Python+RTDL Release-Surface Proposal

## Verdict

Propose `v1.6` as the first historical Python+RTDL public closure milestone,
but do not publish it yet.

`v1.6` should anchor the architecture so the project stops being trapped only
in minor performance optimization loops. This does not lower the priority of
performance work. NVIDIA RT-core performance, `COLLECT_K_BOUNDED` optimization,
true device-memory/zero-copy evidence, and related OptiX work remain top
engineering priorities after the `v1.6` anchor.

The proposed release surface is:

```text
RTDL v1.6 closes the first Python+RTDL architecture track: Python remains the
app/control layer, RTDL owns the RT-shaped primitive contract and bridge to
native Embree/OptiX execution, and the supported public claim is limited to
reviewed RT primitive subpaths rather than arbitrary Python or whole-app
optimization.
```

## Proposed Public Statement

If all closure gates pass, the safe public statement should be:

```text
RTDL v1.6 is the first Python+RTDL architecture milestone. It provides a
Python-hosted eDSL/runtime surface for calling RTDL-managed RT primitives from
Python and executing the supported RT-shaped primitive portion through Embree
and OptiX backends. RTDL does not optimize arbitrary Python code or whole
applications; performance claims remain scoped to exact reviewed primitive
subpaths.
```

This statement should not be used until the remaining closure gates pass and
3-AI consensus explicitly accepts the final release package.

## Included Surface

The proposed `v1.6` included surface is:

- Python-hosted RTDL eDSL/runtime usage from the source tree.
- Embree and OptiX as the active Python+RTDL closure backends.
- Stable primitive boundary:
  `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, and
  `REDUCE_INT(COUNT|SUM)`.
- Same-contract correctness and benchmark evidence for the exact claimed
  primitive subpaths.
- Explicit public distinction between RT primitive acceleration and Python
  continuation work.
- Explicit public distinction between reduced-copy or typed-buffer plumbing and
  true zero-copy.

This included surface must always be read together with the Pending Or Excluded
Surface section below. In particular, naming OptiX as an active backend does
not imply that every `--backend optix` run is a NVIDIA RT-core speedup.

## Pending Or Excluded Surface

The following must remain pending or excluded unless a separate reviewed gate
changes the status:

- `COLLECT_K_BOUNDED` stable primitive promotion.
- Threshold-4 OptiX collect-k gated-candidate public speedup wording.
- True zero-copy wording.
- Partner tensor handoff or DLPack interoperability.
- Package-install support.
- Whole-app speedup.
- Broad database, graph, GIS, ANN, robot, Barnes-Hut, or Jaccard acceleration
  claims.
- Claims that every `--backend optix` run is a NVIDIA RT-core speedup.
- Claims that native internals are fully app-agnostic if compatibility/proof
  paths with app-shaped names or semantics remain.

## Performance Strategy

`v1.6` is an architecture anchor, not a performance freeze.

The project should use `v1.6` to stabilize the public Python+RTDL contract so
future performance work has a clear target. After this anchor, the top
performance priorities remain:

- improving NVIDIA OptiX/RT-core primitive execution;
- continuing `COLLECT_K_BOUNDED` optimization and promotion analysis;
- reducing Python/native and host/device bulk data movement;
- proving or rejecting true device-memory zero-copy paths with measured
  hardware evidence;
- keeping Embree as the CPU same-contract fallback and comparison baseline.

No future performance claim should be broadened merely because `v1.6` exists.
Each claim still needs exact-subpath evidence and external review.

## Closure Gates

Before `v1.6` can be published, these gates must close:

- Formal release-surface proposal accepted by external review.
- Public docs overclaim audit.
- Stable native-path app-leakage audit.
- Blocked-claim regression tests.
- Windows source-tree validation.
- Linux source-tree validation.
- Real NVIDIA OptiX validation for the exact claimed surface.
- Final release package with explicit support matrix and release statement.
- 3-AI consensus for the final release package.
- Explicit user authorization for release/tag action.

## Required Evidence

The final release package should point to:

- Goal 1599 readiness boundary:
  `docs/reports/goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md`
- Goal 1599 3-AI consensus:
  `docs/reviews/goal1599_v1_6_readiness_3ai_consensus_2026-05-09.md`
- Goal 1600 readiness gate:
  `docs/reports/goal1600_v1_6_python_rtdl_readiness_gate_2026-05-09.md`
- Goal 1600 3-AI consensus:
  `docs/reviews/goal1600_v1_6_readiness_gate_3ai_consensus_2026-05-09.md`
- v1.5 release package:
  `docs/release_reports/v1_5/README.md`
- v1.5.1-v2.0 roadmap consensus:
  `docs/reports/three_ai_v1_5_1_to_v2_0_python_rtdl_partner_roadmap_consensus_2026-05-06.md`

Additional closure artifacts must be added before final release.

## Claim Boundary

This proposal does not authorize:

- `v1.6` release;
- release tag action;
- stable `COLLECT_K_BOUNDED` promotion;
- public speedup wording;
- whole-app speedup wording;
- broad RTX/GPU acceleration wording;
- true zero-copy wording;
- partner support claims;
- package-install claims.

## Recommendation

Accept this proposal as the next local `v1.6` planning artifact, then proceed
to the public docs overclaim audit and stable native-path app-leakage audit.

Do not publish `v1.6` yet.
