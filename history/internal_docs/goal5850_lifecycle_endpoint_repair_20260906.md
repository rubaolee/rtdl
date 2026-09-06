# Goal5850 lifecycle-endpoint repair

Date: 2026-09-06

Status: `IMPLEMENTED_LOCALLY__FRESH_FORMAL_TRANSACTION_REQUIRED`

Review status: strict internal hostile self-review only. No external review,
public performance claim, manuscript claim, or cross-generation conclusion is
authorized by this document.

## 1. Why this successor is necessary

The first complete Goal5850 formal transaction at source commit
`95f7d4fc1bcf5fed650ae8c6ab73df77ce1f8db6` retained all 80 formal cells with
zero retry and zero discard, but failed. Its retained archive is
`/workspace/goal5848-ada89-rtx2000-95f7d4fc-transaction1-20260905.failure.tar.gz`
with SHA-256
`d29c0b79bf804d89016eedb3d61f362b48d4061685a3a1e9d737d81e3c4e2cbe`.
Those rows remain adverse evidence and may not be relabeled or pooled.

The transaction exposed two different issues:

1. relation steady execution repeated a 4,096-row Python oracle comparison on
   every prepared call; and
2. the registered post-import endpoint compared processes in different CUDA
   lifecycle states.

The first issue is a real RTDL runtime overhead and has been repaired. The
second is a protocol defect and must not be hidden by moving RTDL work before
the old timer.

## 2. Retained adverse result

At the retained Ada transaction, the registered post-import RTDL/strong-
PyOptix median and worst-block ratios were:

| Task | Median | Worst block | Required |
| --- | ---: | ---: | ---: |
| bounded relation | 1.933x | 2.797x | <=1.20x / <=1.35x |
| weighted triangle | 2.390x | 4.277x | <=1.20x / <=1.35x |

Prepared steady medians were:

| Task | RTDL | Strong PyOptix | Direct OptiX |
| --- | ---: | ---: | ---: |
| bounded relation | 418 us | 585 us | 244 us |
| weighted triangle | 58 us | 59 us | 49 us |

The relation RTDL/Direct ratio was therefore about 1.71x and was a genuine
runtime debt. Triangle was already near the Direct lower bound.

## 3. Runtime repair retained in the successor

The successor precomputes the immutable canonical relation oracle once when a
batch is constructed. Every execution still copies fresh native packed output.
A prior oracle proof may be reused only when both conditions hold:

- the fresh packed bytes exactly match the previously validated output; and
- the exact same immutable canonical oracle object is supplied.

Changed output bytes or a changed oracle always trigger a fresh comparison and
fail closed on mismatch. Native cache-generation and digest checks remain in
the timed public path. No validation-off path, application predicate, or
relation-specific native ABI was introduced.

Exploration on the RTX 2000 Ada pod reduced relation steady medians from about
418 us to 286-295 us. Against the retained same-pod Direct range of about
244-254 us, this predicts roughly 1.13-1.21x; a fresh formal Direct comparison
is still mandatory.

## 4. Falsified startup optimization

One successor attempted to initialize the native OptiX singleton before the
Python CUDA-readiness retain. Six complete balanced exploratory blocks showed
that this was a regression:

| Task | Partial paired median | Worst block |
| --- | ---: | ---: |
| bounded relation | 2.263x | 6.146x |
| weighted triangle | 1.605x | 4.196x |

The native warm interval varied from about 240 ms to 1,002 ms. This ordering
has been removed. The earlier overlap-safe ordering, which runs sealed native-
image admission and CUDA primary-context readiness concurrently before native
OptiX context creation, is restored. Its four-block exploration still failed
the old post-import comparison: relation median 2.277x, triangle median 1.561x.
The failure is retained here; no exploratory row is formal evidence.

One later Strong relation exploratory process consumed one CPU core for more
than four minutes while the GPU was idle and produced no receipt. It was
terminated, and its incomplete output was not converted into a sample. This
was an exploration-only stability incident, not a discarded formal row.

## 5. Causal lifecycle mismatch

The strong arm calls `preload_pyoptix_runtime()` before its post-import timer.
That preload imports `optix`. Fresh-process observation on the Goal5850 pod
showed that `import optix` both creates a current CUDA context and costs:

`853.908, 583.559, 377.725, 595.961, 407.901, 452.869, 507.747, 463.028 ms`

The median is about 485.4 ms, and all eight processes had a non-null current
CUDA context immediately after import.

By contrast, RTDL intentionally does not initialize a GPU merely because its
Python module was imported. Eight fresh direct CUDA-driver probes placed
inside the RTDL post-import lifecycle measured median `cuInit` and primary-
context retain costs of about 223.6 ms and 295.8 ms, respectively. This real
CUDA startup work is inside RTDL's old timer but outside Strong PyOptix's old
timer.

The old endpoint therefore did not compare equivalent lifecycle states. It
measured RTDL from pre-CUDA-context state and Strong PyOptix from post-CUDA-
context state. Moving RTDL initialization into import solely to pass the gate
would be timer gaming and is rejected.

## 6. Lifecycle-corrected endpoint

The versioned successor adds one directly observed wall endpoint for every
Python arm:

`implementation_entry_to_first_correct_result_ns`

It starts immediately before implementation-specific imports and ends after
the first exact public result has been validated. It therefore includes each
arm's real dependency import, CUDA context side effect, artifact/provider
admission, input construction, pipeline/GAS preparation, first execution, and
output validation.

The worker also records:

- `implementation_import_ns`;
- `implementation_import_to_endpoint_gap_ns`; and
- the original `post_import_to_first_correct_result_ns` plus its complete
  phase partition.

Independent validation requires the exact identity:

`implementation endpoint = import + recorded gap + post-import endpoint`.

No interval may disappear. The original post-import ratios remain in every
result and are evaluated against their old 1.20x/1.35x reference as a
non-gating state-mismatch diagnostic.

The corrected primary thresholds are not weakened: median RTDL/Strong remains
`<=1.20x`, and every block remains `<=1.35x`. Prepared RTDL/Direct,
successor/predecessor, Strong/idiomatic, instrumentation, exactness, custody,
compiler-free deployment, and two-generation gates are unchanged.

## 7. Exploratory expectation, not a claim

For four balanced blocks after restoring the safe provider order, summing the
already adjacent import and post-import intervals gave:

| Task | RTDL/Strong median | Worst block |
| --- | ---: | ---: |
| bounded relation | 0.300x | 0.585x |
| weighted triangle | 0.357x | 0.432x |

These values only justify a fresh preregistered transaction. They are not
formal evidence because the source was dirty, the new direct endpoint had not
yet been committed, and only four blocks were observed.

A later four-worker GPU smoke test exercised the versioned v2 receipt itself.
Its RTDL/Strong implementation-entry totals were `916/3540 ms` for relation
and `878/2734 ms` for triangle. The same receipts retained the adverse old
post-import values, `851/412 ms` and `823/399 ms`, respectively. All four exact
decompositions passed with only `10-14 us` of explicitly recorded boundary
gap. RTDL steady medians were `292 us` and `54.7 us`. This test also used a
dirty exploratory source plus prior build artifacts and therefore authorizes
no formal claim.

## 8. Versioning and tests

The successor versions the worker, controller, preregistration, formal process,
formal transaction, preflight, and instrumentation authorities. The
instrumentation gate now measures overhead on the corrected primary endpoint.
The old post-import partition remains independently reconciled.

Tests explicitly require that:

- a coherently resealed lifecycle decomposition mismatch is rejected;
- a post-import diagnostic failure remains visible but does not override a
  passing lifecycle-corrected primary endpoint; and
- a passing post-import diagnostic cannot hide a failing lifecycle endpoint.

The final local checkpoint before commit ran:

- all 121 `goal5848_*_test.py` tests successfully;
- all 92 Goal5845--Goal5847 adjacent regression tests successfully;
- fatal Ruff checks (`E9`, `F63`, `F7`, `F82`) successfully;
- Python bytecode compilation successfully; and
- `git diff --check` successfully.

Full default Ruff still reports historical style findings in the 6,000-line
`v4_rtdlexe.py`; they are not new correctness failures and are deliberately not
mixed into this deadline-critical protocol transaction.

## 9. Mandatory next transaction

Before formal worker zero:

1. commit and push one clean exact source identity;
2. rebuild and bind all source-dependent artifacts;
3. freeze a new preregistration with zero registered timings;
4. run all timer-free correctness, baseline-competence, mutation,
   instrumentation, and AOT-cache gates;
5. execute all 80 formal cells once, with zero retry/discard/pooling; and
6. independently recount every worker, process, raw stream, artifact and gate.

Only a complete passing generation-A transaction permits Goal5851 to run the
identical source commit on a distinct RTX architecture generation. Even two
passing generations remain internal evidence until external review authorizes
specific manuscript wording.
