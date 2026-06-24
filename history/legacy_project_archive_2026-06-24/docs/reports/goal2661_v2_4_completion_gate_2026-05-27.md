# Goal2661: v2.4 Completion Gate

Status: internal v2.4 milestone complete; no public release tag authorized.

Date: 2026-05-27

## Purpose

This goal closes the internal v2.4 engineering milestone that follows the
Goal2657 roadmap consensus.

v2.4 is a protocol-cleanup milestone, not a new public release. Its purpose is
to make v2.5 partner work possible without weakening RTDL's current benchmark
performance basis or allowing app-specific native engine pressure.

## Completed v2.4 Scope

The completed v2.4 scope is:

- typed RTDL primitive handoff buffers;
- prepared-session descriptors;
- segmented/chunked row-streaming contract;
- benchmark metadata integration for RayDB-style grouped reduction, bounded
  witness/contact-manifold, and RT-Graph-style triangle counting;
- machine-readable phase timing metadata for prepared benchmark paths;
- same-contract benchmark performance basis retained from the 10 promoted
  benchmark apps;
- native vocabulary boundary preserved: native primitive symbols stay generic;
- v2.5 direction fixed as Triton-first partner continuation with Numba fallback.

The implementation is centered in:

- `src/rtdsl/partner_protocol.py`
- `src/rtdsl/segmented_row_stream.py`
- benchmark integrations under `examples/v2_0/research_benchmarks/`

The new completion gate is:

- `rtdsl.v2_4_completion_gate()`
- `rtdsl.validate_v2_4_completion_gate()`

## Evidence Chain

The completion gate depends on:

- `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_3ai_consensus_2026-05-27.md`
- `docs/reports/goal2658_v2_4_partner_protocol_foundation_2026-05-27.md`
- `docs/reports/goal2659_v2_4_benchmark_protocol_integration_2026-05-27.md`
- `docs/reports/goal2660_v2_4_phase_timing_metadata_2026-05-27.md`
- this report
- `docs/reports/goal2661_v2_4_completion_claude_review_2026-05-27.md`
- `docs/reports/goal2661_v2_4_completion_gemini_review_2026-05-27.md`
- `docs/reports/goal2661_v2_4_completion_3ai_consensus_2026-05-27.md`

The completion gate records:

- status: `internal_v2_4_complete_no_public_release_tag`;
- protocol version: `rtdl.partner.v2.4`;
- benchmark app count: 10;
- primary comparison row count: 11;
- distinct benchmark-app count and comparison-row count are both validated
  from the benchmark-basis rows;
- promoted-path and opt-in tolerance ratios are locked at 10 percent and
  20 percent respectively;
- hardware basis: NVIDIA RTX A5000 pod evidence;
- public release tag authorized: false;
- package-install claim authorized: false;
- public speedup claim authorized: false.

## Benchmark Basis

v2.4 does not replace the v2.3 benchmark-app performance basis. The current
basis remains the reviewed 10-app / 11-row OptiX-vs-Embree table from the
v2.3 benchmark-performance reports and Goal2657.

The low-margin rows remain explicit protocol-overhead audit targets:

- Hausdorff / X-HD-style;
- Barnes-Hut / RT-BarnesHut-style;
- Robot collision.

Future partner paths must preserve the same phase contract as the accepted
benchmark row before they can replace or become a promoted performance path.

## Boundary Decisions

v2.4 explicitly does not claim:

- package installation support;
- a public release tag;
- new public speedup wording;
- whole-app speedup claims;
- arbitrary PyTorch/CuPy/Triton/Numba acceleration;
- that Triton or Numba replaces OptiX RT traversal.

RTDL owns generic RT traversal and primitive handoff. Partners may own
preparation, continuation, reduction, compaction, finalization, and user-side
postprocessing around those primitives.

Native engines remain app-agnostic. App names and domain semantics such as
RayDB, DBSCAN, Barnes-Hut, triangle counting, contact, robot collision, LibRTS,
RTNN, and Hausdorff remain Python app or documentation vocabulary, not native
engine ABI.

## v2.5 Handoff

v2.5 may now start as:

```text
Python app
  -> Triton/Numba prepares typed columns
  -> RTDL/OptiX performs generic RT-core traversal
  -> Triton/Numba performs generic continuation/reduction/finalization
  -> Python consumes compact results
```

The initial v2.5 partner direction is:

- Triton first;
- Numba fallback or per-pattern alternative where evidence supports it;
- CuPy retained as compatibility/conformance baseline, not the long-term
  ease-of-use target.

v2.5 must not accept a partner path that is easier but significantly slower as
the promoted performance path. Such a path can only be labeled optional,
compatibility, learner/preview, or rejected unless reviewed evidence justifies
promotion.

Every promoted benchmark app that is not piloted in v2.5 must also be
explicitly classified as not attempted, learner/preview only, deferred, or not
suitable for the current partner pattern. Silent omission is not an accepted
v2.5 outcome.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2661_v2_4_completion_gate_test \
  tests.goal2658_v2_4_partner_protocol_test \
  tests.goal2659_v2_4_benchmark_protocol_integration_test
```

Expected result:

```text
OK
```

This focused gate is the v2.4 closure validation. Broad historical unittest
discovery is known to include unrelated legacy drift and is not the v2.4
acceptance criterion.

## Decision

Goal2661 accepts v2.4 as internally complete.

The next engineering milestone is v2.5: implement and measure the first
Triton-first partner continuation path, with Numba fallback where useful,
against the same-contract 10 benchmark-app basis.
