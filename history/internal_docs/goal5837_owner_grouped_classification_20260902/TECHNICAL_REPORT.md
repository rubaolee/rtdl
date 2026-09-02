# Goal5837 Technical Report: Owner-Grouped Successor Classification

Date: 2026-09-02

Status: `COMPLETE__CLASSIFICATION_FROZEN__NO_CLAIM_UPGRADE`

Controlling authority:
`GOAL5837_AUTHORITY.json`

Authority seal:
`025090252ac60b722cc398402297656877405a998024d221592e18aa888f0465`

## Purpose

Goal5837 freezes and classifies the already implemented
`OWNER_GROUPED_ANY_HIT / BOOL_OR` successor route and the bounded linear
RT-CCD evidence that exercises it. It is an evidence and terminology goal,
not a product implementation, GPU execution, stable-API admission, paper
reproduction, or performance goal.

The exact classification is:

`ADDITIONAL_ROOT_EXPORTED_CLOSED_SUCCESSOR_ROUTE__NOT_STABLE_V4_FIXED_CONSTRUCTOR`

## Why this classification is exact

The successor has a closed standard-library callback, a complete public
`compile -> materialize -> prepare -> execute -> close` lifecycle, a verified
generic Boolean owner-grouped behavior, and root-package exports. It therefore
is more than app-private code or an unexposed prototype.

It is not a third stable V4 fixed constructor because all of the following
remain true:

- `rtdsl.v4.ProtocolFamily` contains only
  `custom_aabb_bounded_relation_v1` and
  `builtin_triangle_reduction_v1`.
- `compile_protocol_program` admits only `BoundedRelationProtocol` and
  `TriangleReductionProtocol`.
- `rtdsl.v4.__all__` exports none of the five owner-grouped successor symbols.
- The five successor symbols are exported from the broad root `rtdsl`
  compatibility surface instead.
- No Goal5832 family-shape or protocol-instance document registers this route.
- The route was built before Goal5837 and therefore cannot be retrospectively
  relabelled as a prospective frozen-core new-shape exam.

The count ledger is consequently:

| Denominator | Count |
|---|---:|
| Stable V4 fixed constructors before Goal5837 | 2 |
| Stable V4 fixed constructors after Goal5837 | 2 |
| Additional root-exported closed successor routes | 1 |
| Goal5832-registered successor family shapes | 0 |
| Prospective frozen-core new-shape successes | 0 |

The first two categories and the root-successor category are heterogeneous.
Reporting their sum as "three stable V4 constructors" is forbidden.

## Architecture boundary

The generic behavior is:

```text
accepted event = (query_id, primitive_id)
owner = owner_ids[primitive_id]
owner_hit_bits[owner] |= 1
```

`OWNER_GROUPED_ANY_HIT / BOOL_OR` contains no collision, trajectory, robot,
pose, or RT-CCD semantics. The first physical provider binds this behavior to
OptiX built-in round-linear curves. The trusted wrapper executes real
`optixTrace`, performs `atomicOr` into the owner result, calls
`optixIgnoreIntersection`, and continues traversal. Raw writable pointers and
atomics remain unavailable to restricted Python.

The bounded app owns swept-sphere and obstacle-edge construction, trajectory
identity, collision interpretation, surface-crossing domain admission, and
the independent segment/capsule oracle. Goal5837 verifies that the six
successor RTDL Python modules contain none of the five application terms while
the case-study module retains the collision semantics.

## Evidence frozen by this goal

Goal5837 binds, but does not regenerate or upgrade, these prior results:

- Local source/reference receipt: 6 semantic cases plus 3 scale cases, 9/9
  matches, zero GPU launches, zero performance timings.
- Exact OptiX 8 Pod result: 10 workloads repeated three times, 30/30 true
  OptiX launches, 30/30 independent-oracle matches, and valid prepared-reuse
  receipts.
- Largest functional workload: 512 owners, 4,096 primitives, 1,024 queries,
  4,194,304 independently evaluated pairs, and 1,024 intersecting pairs.
- Exact environment: RTX 4000 Ada, compute capability 8.9, R550.127.05,
  CUDA 12.8, OptiX 8.0.
- OptiX 9 is unavailable on that R550 profile: preflight fails at
  `optixInit_result=7801` before any launch.
- The final six-entry checksum manifest and full evidence tarball are
  reverified, including safe unique archive paths.
- Goal5835 result, Goal5836 A1 authority, and the post-Goal5836 strict audit
  remain byte-identical at their frozen hashes.

Goal5837 itself used no Pod and added zero GPU executions.

## Claim-source matrix

| ID | Disposition | Authorized statement |
|---|---|---|
| C01 | Supported | App-neutral owner-grouped Boolean behavior exists. |
| C02 | Supported | One root-exported closed successor lifecycle exists. |
| C03 | Supported | A bounded linear RT-CCD case study consumes it. |
| C04 | Supported | Exact-profile OptiX 8 functional parity passed 30/30 launches. |
| C05 | Supported | Stable `rtdsl.v4` fixed-constructor count remains two. |
| C06 | Forbidden | It is a third stable V4 fixed constructor. |
| C07 | Not registered | It is a Goal5832 family-shape/protocol instance. |
| C08 | Forbidden | It is a prospective frozen-core generalization success. |
| C09 | Deferred | It has a performance or speedup result. |
| C10 | Forbidden | It is a Paper App or full paper reproduction. |
| C11 | Deferred | Goal5837 has external review or consensus. |
| C12 | Unavailable | It has OptiX 9 functional execution evidence. |

The authority contains a source registry that resolves every `src.*` identifier
used by this matrix to exact source groups, historical input hashes, or
authority fields. Unknown source identifiers fail closed.

## Deterministic verifier

The generator and verifier are
`scripts/goal5837_freeze_owner_grouped_classification.py`. It:

- rejects duplicate JSON keys and non-finite constants;
- checks fixed hashes for historical authorities and GPU artifacts;
- derives stable enum, dispatcher, root export, and lifecycle facts from AST;
- scans the generic Python modules for application-vocabulary leakage;
- verifies local-receipt and authority seals;
- validates all 30 recorded traversal receipts at the required classification
  edge;
- verifies the final checksum manifest and safe archive member paths;
- emits an internally sealed, deterministic authority; and
- exact-compares the stored authority with a fresh reconstruction.

The 18 hostile tests include coordinated reseal attempts that try to create a
third constructor, fabricate prospective success, promote performance/Paper
App/external-review counts, alter GPU execution counts, or change source
identities. All fail closed.

## Regression context

With the isolated Python 3.12 environment, all 186 Goal5833--Goal5837 tests and
all 51 successor tests pass. The local successor receipt and the Goal5835/5836
strict audit also rebuild exactly.

The older Goal5832 module has 22 passing tests and one pre-existing current-tree
custody error. Goal5831 froze the then-current `src/rtdsl/__init__.py` byte
identity; legitimate later root exports changed that mutable file, so the old
validator's repository-wide rehash is not compositional across successor goals.
Goal5837 does not rewrite the historical manifest or claim that this check
passes. Its authority records both identities, uses Goal5832 only as a
hash-bound terminology/count baseline, and independently derives current
stable/root surface facts from AST.

Verification command:

```bash
PYTHONPATH=src:. python3 scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored
PYTHONPATH=src:. python3 -m unittest tests.goal5837_owner_grouped_classification_test
```

## Remaining independent gates

Goal5837 does not consume or satisfy any of these gates:

1. A preregistered Goal5838 new-topology prospective exam.
2. External review after the owner returns from travel.
3. A preregistered Embree/timing study before performance wording.
4. A separate stable-V4 admission transaction if this successor route should
   later become a fixed constructor.
