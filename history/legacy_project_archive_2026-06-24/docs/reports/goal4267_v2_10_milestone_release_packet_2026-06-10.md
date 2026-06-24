# Goal4267 v2.10 Milestone Release Packet

Date: 2026-06-10
Status: final milestone packet pending fresh 3-AI consensus

## Purpose

Goal4267 converts the v2.10 release-candidate draft into a milestone release
packet. It incorporates the Goal4266 large-scale partner evidence and records
the user's 2026-06-10 release decision:

```text
Then go! Make this one a milestone version.
```

This packet is the exact surface that needs final Claude + Gemini + Codex
consensus before the `v2.10` tag is created and pushed.

## Milestone Identity

| Field | Value |
| --- | --- |
| Version label | `v2.10` |
| Release type | source-tree milestone |
| Theme | Python + RTDL + explicit partners over an app-agnostic native engine |
| Last runtime/performance commit before this packet | `0c842eb0` (`Goal4266 publish large-scale partner timing evidence`) |
| Final packet delta | learner-doc refresh, final packet, final consensus/test scaffolding |
| Primary NVIDIA evidence | OptiX/NVIDIA benchmark evidence through Goal4262 plus RTX 3090 partner evidence in Goal4266 |
| Package-install claim | not included |
| AMD/HIPRT claim | not included |
| Embree + Numba CPU partner claim | not included; deferred to v2.11 |

## Scope Of v2.10

v2.10 is the milestone where the Python + RTDL + partner story becomes clean
enough for users to learn from the source tree:

1. The native RTDL engine remains app-agnostic.
2. Users choose the backend and partner explicitly.
3. RTDL primitives are the first choice when they exactly answer the query.
4. CuPy and Numba are documented as explicit partner options for custom
   continuation logic.
5. Benchmark apps are reference implementations and design-pressure workloads,
   not paper-reproduction claims.

## Evidence Chain

| Area | Required evidence |
| --- | --- |
| Ten benchmark front doors | Goal4235 |
| Long-repeat measurement adequacy | Goal4230, Goal4239, Goal4243 |
| Short-row external review | Goal4246, Goal4247 |
| Public-doc claim-boundary scan | Goal4248 |
| Target-map integration and refresh | Goal4249, Goal4261 |
| Post-docs and exact-head pod validation | Goal4250, Goal4262 |
| Internal release-prep packet | Goal4251 |
| Internal release-prep external reviews | Goal4252, Goal4253 |
| Public claim wording candidate and repair | Goal4254, Goal4258 |
| Public claim wording external reviews | Goal4255, Goal4256, Goal4259, Goal4260 |
| Release-candidate draft reviews | Goal4264, Goal4265 |
| Large-scale CuPy-vs-Numba partner evidence | Goal4266 |

Goal4266 matters because it replaces misleading subsecond or missing partner
rows with decision-grade same-contract evidence for the two custom-continuation
families users actually ask about:

| Contract family | Current v2.10 user reading |
| --- | --- |
| RayDB-style unfused grouped count/sum/min/max/avg | CuPy is currently faster on RTX 3090; Numba remains the correct no-RawKernel Python-source reference. |
| Triangle/RayJoin-style compact-mask continuation | CuPy is currently much faster on RTX 3090; Numba remains the correct no-RawKernel Python-source reference. |

Those rows use the same contract, same repeat count, CPU-oracle validation, and
more than one second of aggregate hot time. They are partner-continuation
evidence only.

## User-Facing Documentation Closure

The learner-facing partner docs now say the current v2.10 truth plainly:

- primitive-first when a generic RTDL primitive exactly answers;
- CuPy for current performance on the measured large-scale custom
  continuations;
- Numba when no-RawKernel Python-source reference code matters;
- no partner choice table for primitive-only rows;
- no subsecond row as decision-grade evidence.

Updated pages:

| Page | Reason |
| --- | --- |
| `docs/learn/partner_choice_for_custom_logic.md` | Removes stale "no current CuPy same-contract row" wording and adds Goal4266 decision rule. |
| `docs/learn/benchmark_partner_reference_matrix.md` | Aligns RayDB and triangle compact-mask guidance with Goal4266. |

## Allowed Milestone Wording

Allowed:

```text
RTDL v2.10 is a source-tree milestone for writing Python-hosted RTDL programs
over a generic app-agnostic native engine, with explicit CuPy or Numba partner
continuations where the app needs custom logic.
```

Allowed:

```text
For the measured Goal4266 partner-continuation contracts on RTX 3090, CuPy is
currently faster than the Numba reference implementation; Numba remains useful
when users want Python-source no-RawKernel custom continuation code.
```

## Blocked Claims

This milestone does not authorize:

- package-install product readiness;
- universal speedup;
- broad RT-core speedup guarantee;
- whole-application acceleration guarantee;
- RTDL-beats-RayJoin wording;
- full paper reproduction;
- true-zero-copy product guarantee;
- automatic backend or partner selection;
- AMD/HIPRT performance or parity wording;
- Embree + Numba CPU partner wording;
- app-specific native-engine logic;
- universal CuPy-vs-Numba winner claims.

## Final Release Checklist

| Step | Status | Evidence |
| --- | --- | --- |
| User release decision | done | User requested: "Then go! Make this one a milestone version." |
| Runtime/perf source state | done | Latest runtime evidence commit is `0c842eb0`; Goal4266 is the final runtime/perf addition. |
| Learner docs align with Goal4266 | done | `partner_choice_for_custom_logic.md` and `benchmark_partner_reference_matrix.md` updated. |
| Focused local release tests | pending | Must pass before tagging. |
| Fresh Claude release review | pending | Must review this exact Goal4267 packet and Goal4266 doc refresh. |
| Fresh Gemini release review | pending | Must review this exact Goal4267 packet and Goal4266 doc refresh. |
| Codex final synthesis | pending | Must write a 3-AI consensus file after both reviews exist. |
| Tag and push | pending | Only after focused tests and 3-AI consensus pass. |

## Boundary

Goal4267 is a final milestone packet, not the tag itself. The `v2.10` release
action is allowed only after the fresh 3-AI consensus accepts this exact packet
and the focused release tests pass.
