# Goal4951 Compiled Path-Split RayJoin Gate

Date: 2026-07-04

Status: completed_pending_review

Exit label requested:

`compiled_path_split_correct_but_not_faster_stop`

## Purpose

Gate A/B proved that the internal compiled path-split materializer is generic
and correct on non-RayJoin synthetic fixtures.

This report covers Goal4951 Gate C and Gate D:

- Gate C: wire the compiled materializer into the RayJoin Section 5.7 public
  sample as an app adapter and require byte equality.
- Gate D: compare writer time against the same-run plain writer.

## Files Added For Gate C/D

- `history/internal_docs/goal4951_section57_compiled_path_split_adapter.py`

The adapter is internal. It does not change public RTDL API and does not change
`src/rtdsl/**`.

## Adapter Boundary

The adapter maps RayJoin app state into the generic compiled path-split
contract:

- app chains -> generic chain ids / offsets / counts;
- app line intersections -> generic split events;
- app face labels -> descriptor columns;
- app keep/drop decision -> validity mask;
- app output chain order -> output group ids.

The generic compiled materializer still knows only chains, split events,
descriptor columns, validity, and numeric x/y payloads.

The RayJoin app still owns:

- paper-specific descriptor construction;
- output-chain numbering;
- point-id assignment;
- final text formatting.

## POD Evidence Source State

The POD run used a Git checkout created from the reviewed local HEAD:

```text
HEAD=7d30acd19ab253116fe210949918ec2bb5b987a8
```

The checkout was augmented only with Goal4951 files and required ignored run
inputs/artifacts:

- `history/internal_docs/goal4951_compiled_path_split_spike.py`
- `history/internal_docs/goal4951_section57_compiled_path_split_adapter.py`
- `tests/goal4951_compiled_path_split_spike_test.py`
- public-sample data under `_data/public_sample/`
- local `build/librtdl_optix.so`

## Artifacts Pulled Back Locally

- `history/internal_docs/goal4951_pod_artifacts/plain_section57_overlay.json`
- `history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_first.json`
- `history/internal_docs/goal4951_pod_artifacts/compiled_section57_overlay_rerun.json`

All three generated outputs have SHA-256:

```text
464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e
```

which matches the public answer file.

## Gate C: Correctness

Gate C passed.

| Route | Byte Equal To Answer | Bytes | Lines |
| --- | ---: | ---: | ---: |
| plain `section57_overlay.py` | true | 16,631,243 | 737,830 |
| compiled path-split first run | true | 16,631,243 | 737,830 |
| compiled path-split rerun | true | 16,631,243 | 737,830 |

The compiled adapter therefore preserves Section 5.7 public-sample output
correctness.

## Gate D: Performance

Gate D failed.

Same-cache POD writer times:

| Route | Writer Seconds | Relative To Plain |
| --- | ---: | ---: |
| plain `section57_overlay.py` | 2.583328 | 1.000x |
| compiled path-split first run | 4.207148 | 0.614x |
| compiled path-split rerun | 4.155936 | 0.622x |

The approved minimum useful gate was:

```text
writer speedup >= 1.10x
```

The rerun achieved:

```text
2.583328 / 4.155936 = 0.622x
```

That is a regression, not a win. The route is correct but slower.

## Rerun Phase Breakdown

Compiled adapter writer subphases on the rerun:

| Subphase | Seconds |
| --- | ---: |
| `build_path_split_inputs_map0_sec` | 0.181392 |
| `build_path_split_inputs_map1_sec` | 0.141822 |
| `compiled_path_split_materialize_map0_sec` | 1.882143 |
| `compiled_path_split_materialize_map1_sec` | 0.507788 |
| `format_compiled_path_split_map0_sec` | 0.734017 |
| `format_compiled_path_split_map1_sec` | 0.572281 |
| `bulk_write_text_sec` | 0.043196 |

Grouped summary:

| Group | Seconds |
| --- | ---: |
| input build | 0.323214 |
| compiled generic materialization | 2.389931 |
| app text formatting | 1.306298 |
| final file write | 0.043196 |

The same lesson from Goal4937/4940 reappears in a compiled form:

- byte-equality is achievable;
- final file write is tiny;
- the generic row materialization / descriptor transfer path is still too heavy;
- the route does not beat the plain handwritten app writer.

## Decision

Per the approved Goal4951 kill condition:

> If byte-equal but slower, the route is killed and not retained as default.

Therefore:

- do not promote the compiled path-split adapter;
- do not expose a public API from this spike;
- do not retain it as a default RayJoin route;
- keep the evidence and code only as internal experiment material unless the
  owner explicitly requests further architecture work.

## What This Proves

It proves:

- the generic compiled materializer can preserve RayJoin output correctness;
- the adapter boundary is feasible;
- this CPU/Numba materializer path is not a performance solution for the public
  sample writer.

## What This Does Not Prove

It does not prove:

- that all Layer 3 ideas are dead;
- that a native C++ or device-resident writer cannot win;
- that RayJoin performance is finished;
- any public release or speedup claim.

It only rejects this specific implementation route:

```text
app adapter -> Numba CPU compiled generic path-split materializer -> Python text formatter
```

## Proposed Next Step

Close Goal4951 as:

```text
compiled_path_split_correct_but_not_faster_stop
```

Before any new Layer 3 attempt, require a new goal and review. The next attempt
must not be another CPU/Python row materializer wrapper. It would need to target
one of the remaining structural causes directly:

- native compiled output-chain construction;
- device-resident row-buffer transfer into a compiled writer;
- or a deliberate decision to stop RayJoin-specific performance work and keep
  the current correct reproduction route.
