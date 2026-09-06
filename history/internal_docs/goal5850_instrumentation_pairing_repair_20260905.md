# Goal5850 instrumentation-pairing repair

Date: 2026-09-05 America/New_York

Status: `FAILURE_RETAINED__V2_ESTIMATOR_IMPLEMENTED__FRESH_TRANSACTION_PENDING`

## 1. Decision

The first Goal5850 transaction at source commit
`4bd4c6b5e4b04c2690f0cc0ebcc585a9509f6667` is a retained failure. It
completed all 32 instrumentation workers but failed the triangle 5% overhead
gate before formal worker zero. No result from that transaction may be relabeled,
retried in place, discarded, pooled, or evaluated as a Goal5850 pass.

The failure exposed a methodological defect in the v1 instrumentation
protocol. The schedule was explicitly paired and order-balanced by block, but
the estimator discarded the pairs: it separately took the ON and OFF marginal
medians and then subtracted them. Fresh-process endpoint noise changed sample
rank enough to create a false 18.7567% point estimate even though the median of
the eight registered within-block ON/OFF ratios was 0.989446x.

The repair keeps the endpoint, 5% threshold, tasks, block count, process
isolation, order balancing, cache policy, and all formal experiment rules
unchanged. It versions the instrumentation authority as v2 and computes, per
task:

1. one `ON / OFF` ratio in each preregistered block;
2. the integer median of those eight within-block ratios; and
3. `max(0, median_ratio - 1.0)` as measured instrumentation overhead.

This is the same pair-first estimator structure used by the primary Goal5848
comparisons. A completely new transaction must establish whether v2 passes.

## 2. Retained failed transaction

| Field | Value |
| --- | --- |
| GPU | NVIDIA RTX 2000 Ada Generation |
| GPU UUID | `GPU-2fe387f0-ed74-e62c-0686-750461318361` |
| Compute capability | `8.9` |
| Driver | `570.195.03` |
| Source commit | `4bd4c6b5e4b04c2690f0cc0ebcc585a9509f6667` |
| Source tree | `e9a4458fca800e88dfe75b344c77d497dad7c8aa` |
| Predecessor commit | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` |
| Preregistration seal | `a8085cf996a792c9831d8f3c9ef14698785fd4644e45a5d8fa20f7b1a17de4bb` |
| Failure seal | `5a2aa8a0a93334bfc76d70d95fde3baa5d03efe6f3da32f45f081e4b4aa089d0` |
| Failure archive SHA-256 | `987f6d79c27b4f3f19d2010322a6b652f56ee7c77b47a02aa56534c50c06e9a0` |
| Timer-free workers | 8/8 passed |
| Competence workers | 4/4 passed |
| Instrumentation workers | 32/32 completed |
| Formal timing cells | 0/80 started |
| Retry/discard | 0/0 |

The archive and its hash were copied off the pod and independently rehashed at
the same digest. The local custody root is outside Git under
`/Users/rl2025/goal5848_evidence/ada89_rtx2000_4bd4c6b5_transaction1_20260905/`.

## 3. Gates passed before the failure

The exact AOT reuse authority passed for both tasks:

| Task | Cold first resolution | Fresh-process hit median | Hit/cold |
| --- | ---: | ---: | ---: |
| Relation | 21.691 s | 162.442 ms | 0.007489x |
| Triangle | 11.104 s | 159.032 ms | 0.014322x |

The timer-free authority reported
`PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES` with eight workers, eight
processes, zero retries, and zero discards.

The nonformal strong-baseline competence gate also passed:

| Task | Idiomatic Pyoptix | Strong Pyoptix | Strong/idiomatic | Limit |
| --- | ---: | ---: | ---: | ---: |
| Relation | 2,523,372 ns | 579,109 ns | 0.229498x | 1.05x |
| Triangle | 89,630 ns | 57,785 ns | 0.644706x | 1.05x |

These values remain nonformal engineering evidence and are not part of any
formal performance estimator.

## 4. Raw instrumentation evidence

### Triangle

| Block | OFF ns | ON ns | Signed difference ns | ON/OFF |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 811,136,750 | 1,117,632,732 | 306,495,982 | 1.377860x |
| 1 | 1,694,859,156 | 1,132,674,454 | -562,184,702 | 0.668300x |
| 2 | 1,220,303,602 | 484,672,493 | -735,631,109 | 0.397174x |
| 3 | 950,333,677 | 714,413,983 | -235,919,694 | 0.751751x |
| 4 | 605,712,541 | 1,355,396,053 | 749,683,512 | 2.237689x |
| 5 | 993,487,747 | 773,662,335 | -219,825,412 | 0.778734x |
| 6 | 825,578,463 | 1,355,979,543 | 530,401,080 | 1.642460x |
| 7 | 869,980,562 | 1,044,114,168 | 174,133,606 | 1.200158x |

The v1 marginal medians were 910,157,119 ns OFF and 1,080,873,450 ns ON,
which produced the failing 18.7567% estimate. The within-block ratio median is
0.989446x, so the v2 overhead projection is 0%. This projection is diagnostic
only; it does not convert the failed transaction into a pass.

### Relation

| Block | OFF ns | ON ns | Signed difference ns | ON/OFF |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1,100,116,162 | 966,907,298 | -133,208,864 | 0.878914x |
| 1 | 471,428,048 | 1,296,585,492 | 825,157,444 | 2.750336x |
| 2 | 1,151,878,122 | 1,187,760,309 | 35,882,187 | 1.031151x |
| 3 | 1,001,909,448 | 898,805,857 | -103,103,591 | 0.897093x |
| 4 | 1,176,339,893 | 807,256,725 | -369,083,168 | 0.686244x |
| 5 | 1,237,395,322 | 1,081,202,855 | -156,192,467 | 0.873773x |
| 6 | 1,129,411,148 | 960,054,696 | -169,356,452 | 0.850049x |
| 7 | 387,875,616 | 1,320,753,854 | 932,878,238 | 3.405096x |

The relation v1 marginal estimator already projected 0% overhead. Its
within-block ratio median is 0.888003x. The large positive and negative paired
values show why the process-start endpoint needs the registered pairing rather
than rank-independent marginal medians.

## 5. Root cause and scope

This was not measured 18.8% timer cost. The ON path did not consistently run
slower: four triangle blocks were faster and four were slower. The observed
fresh-process endpoint range was approximately 0.485--1.695 seconds, orders of
magnitude larger than individual phase-clock operations. The v1 marginal
estimator paired neither the values nor their local launch conditions, despite
collecting an order-balanced pair in every block.

The v1 evaluator did implement its literal estimator string, so the correction
is a protocol-version repair, not a claim that old bytes were evaluated
incorrectly after the fact. The old result remains adverse evidence.

No production runtime, compiler, native kernel, application behavior, timed
formal path, task input, expected output, threshold, sample-retention rule, or
performance gate changes in this repair.

## 6. Bias controls

The repair occurs after observing a failure and therefore has post-hoc risk.
The following controls are mandatory:

- retain and cite the complete v1 failure;
- use an explicit v2 authority schema and estimator string;
- commit before collecting any new v2 worker;
- start from a new output root and new preregistration;
- keep all eight blocks and all 32 fresh processes;
- keep the 5% threshold unchanged;
- do not reuse any v1 endpoint in v2;
- preserve every v2 stdout/stderr and receipt; and
- submit the method change to later external review before paper use.

Rerunning v1 until random endpoint ordering passes is forbidden.

## 7. V2 acceptance

The replacement transaction may proceed only when local tests prove:

- the authority schema is v2;
- each task has exactly one ON and one OFF worker for every block;
- each block records an exact integer `ON/OFF` ratio;
- the reported median is the integer median of the eight block ratios;
- overhead is `max(0, median_ratio - 1,000,000 ppm)`;
- the v2 authority binds all 32 worker receipts, all 32 process receipts, and
  every worker JSON/stdout/stderr file by SHA-256;
- preflight recomputes the estimator from authority-bound rows rather than
  trusting the producer's pass bit;
- the final transaction authority independently reopens the 32 worker files
  and 96 process files, verifies exact command/stdout/stderr/phase evidence,
  and recomputes the same task summaries;
- a synthetic rank-crossing case that fails marginal medians is correctly
  evaluated by its registered pairs; and
- a uniform 6% overhead still fails the unchanged 5% gate.

Goal5850 remains open until a completely fresh transaction passes all original
gates and produces a byte-identical independent authority recount.
