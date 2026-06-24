# Goal3422 Closed-Shape Topology Refinement Gap

Status: diagnostic completed on NVIDIA RTX A5000 pod.

## Why This Goal Exists

Goals 3420 and 3421 tested the next v2.8 idea after native page plans:
produce pair columns on device, refine them on device, then feed grouped
continuations. The result is precise:

- RT traversal already gives a strong device-resident superset.
- A simple point-in-ring device predicate is not enough to reproduce the current
  host GEOS/topology oracle.
- The next primitive must model closed-boundary/topology semantics explicitly.

## Evidence

Full public RayJoin CDB, 16,545 probe points and 15,700 closed shapes:

| Path | Pair rows | Pair relation to host | Group relation to host |
| --- | ---: | --- | --- |
| Host exact oracle | 47,262 | authority | authority |
| RT device predicate candidates | 47,570 | 0 missing, 308 extra | 248 mismatched groups |
| RT candidates + CuPy simple-ring refine (`point_eps=1e-9`) | 47,045 | 217 missing, 0 extra | 97 mismatched groups |

Tolerance sweep for the CuPy simple-ring filter:

| point_eps | refined rows | pair match | group match | mismatched groups |
| ---: | ---: | --- | --- | ---: |
| 1e-12 | 47,045 | false | false | 97 |
| 1e-10 | 47,045 | false | false | 97 |
| 1e-9 | 47,045 | false | false | 97 |
| 1e-8 | 47,045 | false | false | 97 |
| 1e-7 | 47,045 | false | false | 97 |
| 1e-6 | 47,052 | false | false | 102 |

Feature bucket over unique RT candidate pairs:

| same chain | simple ring | shared nonzero face | in host oracle | count |
| --- | --- | --- | --- | ---: |
| false | true | true | true | 30,519 |
| true | true | true | true | 15,640 |
| false | true | false | true | 886 |
| false | false | true | false | 194 |
| false | false | false | false | 114 |
| false | false | false | true | 112 |
| false | false | true | true | 45 |

Interpretation:

- Simple ring refinement has no observed false positives in this diagnostic, but
  it is a strict subset of the host oracle.
- Shared-face topology recovers some host-only pairs, but also admits false
  positives, so `simple OR shared_face` is not a valid exact rule.
- The current host oracle is a closed-boundary/topology semantics surface, not a
  plain point-in-ring surface.

## Next Engineering Target

Build a topology-aware closed-boundary refinement contract:

```text
RT broad-phase candidate pair columns
-> device/partner closed-boundary topology refinement
-> exact pair columns for grouped continuations
```

The next implementation must:

1. Keep RTDL native traversal app-agnostic.
2. Treat topology rows as caller-provided data, not native app policy.
3. Keep host GEOS/topology exact rows as the oracle during validation only.
4. Fail closed unless the refined pair multiset and grouped counts match the
   oracle.
5. Continue blocking release, RT-core speedup, true-zero-copy, and default-route
   claims until pod evidence and external review land.

## Boundary

Goal3422 does not solve the exact predicate. It rules out the tempting but wrong
solution: "just run a double point-in-ring kernel." The v2.8 path now needs a
generic topology-aware refinement primitive or a conscious decision to define a
different public closed-shape semantics than the current GEOS/topology oracle.
