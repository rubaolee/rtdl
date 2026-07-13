# Goal4982 Result: Symmetric Fresh/Warm Isolation For LSI Producer And Carrier Builder

Date: 2026-07-04

## Verdict

```text
completed_lsi_and_carrier_warmup_symmetric_matrix__lsi_still_dominates
```

Goal4982 completed the symmetric isolation requested by Claude's v2.14.3 closeout-plan review.

The result is not a new speed headline. It is a boundary correction:

- the grouped carrier cold/first-large-call cost can disappear after warm state;
- the LSI producer cost remains about `2.7s` in repeated full-route runs;
- the LSI repeat diagnostic that reports `0.000000s` is not accepted as valid timing evidence;
- therefore v2.14.3 must not present a warm-only number that warms carrier while silently keeping or excluding LSI setup.

## Inputs And Artifacts

Artifacts are stored under:

```text
history/internal_docs/goal4982_lsi_carrier_fresh_warm_artifacts_2026-07-04/
```

Files:

```text
fresh_with_lsi_repeat_diagnostic.json
full_route_repeat_1.json
full_route_repeat_2.json
```

Workload:

```text
top4_county_zipcode_arcgis_same_source
```

Route:

```text
writer-free binary route
bounded exact LSI device columns
point-location device face columns
fast scaled-point host pack
compiled grouped carrier
```

## Symmetric Timing Matrix

### Full Route Repeats

| Artifact | Hot body sec | LSI producer sec | Downstream sec | Carrier sec | Side0 sec | Side1 sec |
|---|---:|---:|---:|---:|---:|---:|
| `fresh_with_lsi_repeat_diagnostic.json` | 3.668801 | 2.692300 | 0.972703 | 0.111014 | 0.021188 | 0.077678 |
| `full_route_repeat_1.json` | 3.670935 | 2.763328 | 0.904126 | 0.105219 | 0.019586 | 0.074569 |
| `full_route_repeat_2.json` | 3.620381 | 2.706508 | 0.910247 | 0.104357 | 0.019722 | 0.073564 |

### LSI Extended Timings

| Artifact | LSI total sec | Scaled cache ensure | Grouped range ensure | Exact pipeline ensure | Split kernel ensure | Device alloc | Native launch |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fresh_with_lsi_repeat_diagnostic.json` | 2.691371 | 0.686865 | 1.029486 | 0.527834 | 0.441727 | 0.003088 | 0.002288 |
| `full_route_repeat_1.json` | 2.762878 | 0.715956 | 1.060821 | 0.534130 | 0.448292 | 0.001335 | 0.002266 |
| `full_route_repeat_2.json` | 2.706030 | 0.704267 | 1.047109 | 0.523727 | 0.427250 | 0.001338 | 0.002264 |

## Interpretation

### 1. Carrier Is Warm-State Small In These Runs

The grouped carrier builder is about `0.104-0.111s` in the repeated full-route runs.

This confirms the Goal4981 correction: the previous `~0.69s` carrier side-builder cost was a first-large-call / warmup artifact, not a stable side-order algorithm win. It is legitimate to discuss carrier warm state, but only with fresh and warm shown side by side.

### 2. LSI Producer Still Dominates The Full Route

The LSI producer remains about `2.69-2.76s` across all full-route runs. It is still the dominant cost in the writer-free binary route.

The largest LSI sub-costs are not native launch or device allocation:

- grouped range ensure: about `1.03-1.06s`;
- scaled cache ensure: about `0.69-0.72s`;
- exact pipeline ensure: about `0.52-0.53s`;
- split kernel ensure: about `0.43-0.45s`;
- native launch: about `0.0023s`.

This means the main LSI cost is setup / ensure / producer work, not the final device launch itself.

### 3. The `0.000000s` LSI Repeat Diagnostic Is Not Timing Evidence

`fresh_with_lsi_repeat_diagnostic.json` contains an LSI repeat diagnostic:

| Repeat | Wall sec | Native sec | Rows |
|---:|---:|---:|---:|
| 0 | 0.000000 | 0.000000 | 428322 |
| 1 | 0.000000 | 0.000000 | 428322 |
| 2 | 0.000000 | 0.000000 | 428322 |

This is not accepted as valid LSI warm timing evidence.

The plausible explanations are:

- the diagnostic is replaying cached metadata/results without timing the producer path;
- the timer is attached to the wrong code path;
- the repeated diagnostic is too narrow to represent full-route LSI production.

Therefore Goal4982 explicitly rejects the `0.000000s` diagnostic as a performance headline or as proof that LSI producer cost has been eliminated.

### 4. The Honest Current State

Current top4 writer-free binary route after Goal4977-4981:

```text
hot body:        about 3.62-3.67s
LSI producer:    about 2.69-2.76s
downstream:      about 0.90-0.97s
carrier builder: about 0.10-0.11s in warm-state repeated runs
```

This is better than the pre-Goal4977 route, but it is not a solved high-performance route.

The remaining large target is now the LSI producer, not carrier side order.

## Claim Boundary

Authorized:

- report fresh and warm state side by side;
- say carrier first-large-call cost is not a stable algorithm cost;
- say current repeated full-route LSI producer remains about `2.7s`;
- target LSI producer setup/reuse as the next meaningful performance problem;
- keep writer-free binary route as the v2.14.3 bounded performance line.

Not authorized:

- no warm-only headline;
- no author-performance claim;
- no `0.000000s` LSI replay claim;
- no claim that LSI producer is solved;
- no claim that v2.14.3 reaches author overlay performance;
- no RTDL core/native promotion from this measurement alone.

## Impact On Remaining v2.14.3 Goals

Goal4982 answers Claude's A1/A2/A3:

- LSI and carrier were measured symmetrically;
- carrier warmup is characterized;
- LSI producer cold/warm is not solved and remains in the fresh route;
- any final v2.14.3 matrix must show fresh and warm columns explicitly;
- if a warm route is used, it must name the real product behavior that justifies it.

## Recommended Next Goal

Goal4983 should decide the allowed warmup / prepare strategy.

It must answer:

1. Is LSI producer setup reusable in a real `prepare-once/query-many` product route?
2. If yes, how is that route exposed without making RayJoin-specific RTDL core semantics?
3. If no, does the `~2.7s` LSI producer stay in the fresh headline?
4. Should the broken/invalid LSI repeat diagnostic be repaired or removed?

Expected labels for Goal4983:

```text
authorized_product_prepare_once_query_many_with_fresh_and_warm_matrix
```

or

```text
warmup_not_product_strategy_keep_fresh_lsi_headline
```

or

```text
repair_lsi_repeat_diagnostic_before_matrix
```
