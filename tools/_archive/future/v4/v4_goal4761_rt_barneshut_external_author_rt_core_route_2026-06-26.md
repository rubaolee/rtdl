# Goal4761: RT-BarnesHut Same-Semantics External Author RT-Core Route

Date: 2026-06-26

Status: complete as external author RT-core reference route; not complete as native V4 operator.

## Decision

Goal4760 created the author-contract semantic gate. Goal4761 adds a runnable same-input RT-core execution route through the authors' `rtbarneshut` binary, wrapped by V4 code with strict claim boundaries.

This is deliberately named `external_author_rt_core_reference_route`. It is a real RT-core execution route and it validates force checksum against the RTDL author-semantics CPU oracle. It is **not** a native V4 operator implementation, and it does **not** authorize V4 performance claims.

## Code Added

- `src/rtdsl/v4_rt_barneshut_author_route.py`
  - `run_v4_rt_barneshut_external_author_rt_core_route`;
  - route dataclasses;
  - checksum validation against the Goal4760 CPU oracle;
  - phase timing schema;
  - hard non-native/non-release claim boundary.

- `scripts/v4_rt_barneshut_author_route_probe.py`
  - CLI runner for the external author RT-core route.

- `tests/v4_goal4761_rt_barneshut_author_route_test.py`
  - verifies route payload;
  - verifies checksum mismatch fails validation;
  - verifies CLI output;
  - verifies no V4 performance claim is authorized.

## Validation

Local:

```text
py -m unittest tests.v4_goal4761_rt_barneshut_author_route_test
Ran 3 tests in 1.476s
OK
```

POD:

```text
cd /root/rtdl_v4_candidate_pod
/root/rtdl_v4_venv/bin/python -m unittest tests.v4_goal4761_rt_barneshut_author_route_test
Ran 3 tests in 0.656s
OK
```

## POD Route Evidence

Evidence directory:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/`

| Evidence | Points | Route kind | RT-core execution | Native V4 operator | RT force | Execution | Checksum relative error |
|---|---:|---|---|---|---:|---:|---:|
| `v4_rt_barneshut_author_route_4096.json` | 4,096 | `external_author_rt_core_reference_route` | yes | no | 0.043450s | 0.294775s | `1.933403535816373e-06` |
| `v4_rt_barneshut_author_route_8192.json` | 8,192 | `external_author_rt_core_reference_route` | yes | no | 0.007433s | 1.516020s | `2.450123881979025e-07` |

Both rows use the same author-format input contract and validate RT output checksum against the RTDL CPU oracle from Goal4760.

## Why This Matters

Before Goal4761:

- we had authors' binary runs;
- we had a CPU semantic oracle;
- we did not have a V4-controlled route payload that executed the author RT-core path and emitted V4-compatible evidence fields.

After Goal4761:

- V4 can run a same-input RT-core reference route;
- checksum parity is machine recorded;
- phase seconds are in a stable schema;
- claim boundaries prevent this from being sold as a native V4 speed win.

## What This Still Does Not Solve

This is not the final V4 RT-BarnesHut implementation.

Remaining gap:

1. The route calls the authors' binary externally.
2. The route does not expose a native RTDL operator for the Barnes-Hut traversal.
3. V2.14/V3.0.2 do not have this author-contract route in their release tags.
4. A fair V2/V3/V4/author speed table is still blocked until the native route or an explicitly accepted compatibility-backport strategy exists.

## Next Goal

Goal4762 should decide and implement one of two honest paths:

1. **Native V4 route path:** port or bind the author-compatible 3D RT-BarnesHut traversal into RTDL's native V4 operator/runtime surface.
2. **Reference-adapter path:** keep Barnes-Hut as an external-author reference route and exclude it from V4-native speed wins, while using it as a correctness/performance baseline for future native work.

The first path is the only one that can eventually support a native V4 Barnes-Hut speed claim.

## Goal-Level Decision Audit

1. Was I being stupid?
   - Not in the implementation, but the risk was real: calling an external author binary could become another overclaim if not named precisely.

2. What action would make it stupid?
   - Marking this as `native_v4_operator=true` or using it as V4-over-author speed evidence.

3. Is there another path that avoids getting stuck on a bad premise?
   - Yes: label it as an external author RT-core reference route and reserve native V4 claims for a later native route.

4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4762 must either implement the native route or explicitly classify Barnes-Hut as reference-adapter-only for V4.0.

## Non-Authorization

Goal4761 does not authorize:

- native V4 Barnes-Hut operator claims;
- V4-over-author speedup claims;
- V2/V3/V4 fair performance table claims;
- public RT-BarnesHut paper reproduction wording;
- V4 release wording based on Barnes-Hut.

It authorizes only:

> V4 now has a same-semantics external author RT-core reference route with checksum parity against the RTDL author-contract CPU oracle. Native V4 RT-BarnesHut remains open.
