# Goal5850 RTX generation A final internal report

Date: 2026-09-06

Decision:
`PASS__GOAL5850_GENERATION_A_COMPLETE__GOAL5851_REQUIRED`

Review state: strict internal review only. External review is incomplete and
no public or manuscript performance claim is authorized by this report.

## 1. Scope and conclusion

Goal5850 required one complete formal Goal5848 transaction on the first RTX
generation. The successful transaction used exact clean source commit
`c4351f6120d1d73d7c2b72ff4d61ad747061f836`, tree
`1faf8ca2a99e4c1011443942479e2edf7b297edb`, and predecessor commit
`12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`.

It completed every preregistered stage on one NVIDIA RTX 2000 Ada Generation
GPU (compute capability 8.9), retained all 80 formal cells and 10,240 steady
samples, used zero retries and zero discards, passed both tasks' frozen
correctness and performance gates, and produced two byte-identical independent
single-generation authorities.

This completes Goal5850 only. Goal5848 is not cross-generation complete until
Goal5851 repeats the identical `c4351f612...` source on a different RTX
compute-capability generation and GPU UUID and builds the non-pooled
cross-generation authority.

## 2. Preserved failure chain

The successful transaction does not replace or relabel prior failures.

| Transaction | Source | Terminal result | Retained archive SHA-256 |
| --- | --- | --- | --- |
| 1 | `95f7d4fc...` | All 80 cells retained; old post-import gate failed because RTDL and PyOptix entered the timer in different CUDA lifecycle states | `d29c0b79bf804d89016eedb3d61f362b48d4061685a3a1e9d737d81e3c4e2cbe` |
| 2 | `70f85796...` | Controller passed all 80 cells; independent authority rejected the honest Direct native runtime sentinel | `fde22b987fdaf9b3617e9371ebb391254fa856eb2495688006ca54acf60d99fc` |
| 3 | `8f7b640a...` | All 80 cells retained; relation public RTDL/Direct median was `1.209372x`, above the unchanged `1.20x` gate | `412454f05b6bebbc0419f2468a7a7462248a5a1c613b53bd675dc99107d8f707` |
| 4 | `c4351f612...` | Complete single-generation pass | `f487f42580ac8cb81c202fe867b976ba7a267b9ca7ccffb980c626d775b112c8` |

Transaction 3's relation block ratios were
`[1.205890, 1.216685, 1.212854, 1.219244, 1.204127, 1.236526,
1.162223, 1.168937]`. Its failure is close to the threshold but remains a
failure. No row from any failed or exploratory run was pooled into transaction
4.

## 3. Final repair before the passing transaction

### 3.1 Measured problem

The prepared relation replay crossed the Python/native ABI twice per public
execution:

1. `_native_source_cache_digest()` looked up the prepared token, acquired the
   native owner lock, copied a 32-byte digest, and created fresh ctypes digest,
   presence, and 16 KiB error buffers.
2. The v7 execute call repeated token lookup and owner-lock acquisition before
   executing the actual operation.

Direct OptiX crossed the ABI only once. Transaction 3 missed the median gate by
`0.009372x`, so this redundant boundary was material at the measured scale.

### 3.2 Generic v9 repair

The successor adds
`rtdl.v4.prepared_bounded_relation_callback.v9` without changing relation
semantics.

- Immutable tuple and typed-buffer batch front doors precompute a stable
  32-byte ctypes representation of their already required SHA-256 identity.
- The fast public replay uses local immutable batch identity to request reuse
  and passes that exact digest to the execute ABI.
- Native v9 requires a non-null 32-byte digest and compares it with the
  committed native cache digest while holding the same owner mutex used by the
  execution.
- A missing, malformed, uncommitted, or mismatched digest fails closed before
  cached data can execute.
- Diagnostic execution retains the separate digest query. Existing v5-v8
  exports remain available, and v7 artifacts remain admissible for backward
  compatibility.

The change removes one FFI/registry/lock round trip; it does not remove cache
identity validation. It is expressed in the generic prepared bounded-relation
owner and contains no RayDB, collision, graph, paper-app predicate, or other
application dispatch.

No workload, output contract, baseline, timer, estimator, threshold, block
schedule, sample count, correctness check, or evidence requirement changed.

## 4. Pre-formal validation

Before transaction 4:

- 66 focused cache, ABI, overflow, and adjacent tests passed with three
  declared environment skips.
- All 128 Goal5848 tests passed under ordinary Python.
- All 128 Goal5848 tests passed under `python -O`.
- The Goal5844-Goal5848 adjacent suite passed 262/262.
- The new test passed default Ruff; touched Python passed fatal Ruff selectors
  `E9,F63,F7,F82`; compileall and `git diff --check` passed.
- An exploratory pod build exported v9 and returned
  `PASS__MINIMAL_RTDLEXE_AOT_NATIVE`.

The full default Ruff scan of touched legacy modules still reports unrelated,
pre-existing style debt. It is not silently represented as clean and was not
reformatted during the experiment freeze.

## 5. Formal transaction

### 5.1 Hardware and source

| Field | Exact value |
| --- | --- |
| GPU | NVIDIA RTX 2000 Ada Generation |
| Compute capability | 8.9 |
| GPU UUID | `GPU-2fe387f0-ed74-e62c-0686-750461318361` |
| Memory | 16,380 MiB |
| Driver | 570.195.03 |
| Source commit | `c4351f6120d1d73d7c2b72ff4d61ad747061f836` |
| Source tree | `1faf8ca2a99e4c1011443942479e2edf7b297edb` |
| Predecessor | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` |

The checkout was detached and clean. Current and predecessor native AOT
profiles both built with `PASS__MINIMAL_RTDLEXE_AOT_NATIVE`.

### 5.2 Gate population

- Exact AOT reuse: 10 fresh processes, zero retry/discard,
  `PASS__AC8_EXACT_FRESH_PROCESS_AOT_REUSE`.
- Timer-free correctness: eight primary arm/task processes, zero
  retry/discard, `PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES`.
- Strong-baseline competence: four fresh processes, zero retry/discard,
  `PASS__STRONG_PYOPTIX_COMPETENT_FOR_BOTH_TASKS`.
- Instrumentation qualification: 512 fresh processes, 16 replicates per
  task/block/mode, zero retry/discard, no samples included in formal
  estimators.
- Formal transaction: two tasks by five arms by eight balanced blocks equals
  exactly 80 fresh worker processes. Each retained 128 steady samples, for
  10,240 total; retry and discard counts were zero.

Instrumentation ON/OFF paired-ratio medians were `0.966297x` for triangle and
`0.975242x` for relation. The preregistered non-negative overhead estimator was
therefore 0 ppm for both, below the unchanged 50,000 ppm limit. The raw block
ratios, including blocks above 1.0, remain in the authority.

## 6. Results

The primary lifecycle ratio begins before implementation-specific imports. The
old post-import endpoint is retained as a mandatory non-gating adverse
diagnostic. Steady comparisons are within-machine prepared executions.

| Task | RTDL/Strong lifecycle median | Lifecycle worst block | Old post-import median | Old post-import worst | RTDL/Direct steady median | Strong/idiomatic steady median | Successor/predecessor steady median |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| checked-U64 weighted triangle | `0.327669x` | `0.414433x` | `1.997967x` FAIL diagnostic | `2.526119x` | `1.171933x` PASS | `0.658855x` PASS | `0.684053x` PASS |
| bounded AABB relation | `0.389597x` | `0.423498x` | `2.111030x` FAIL diagnostic | `4.118098x` | `1.075168x` PASS | `0.231363x` PASS | `0.643587x` PASS |

Prepared steady medians, aggregated over the eight worker medians, were:

| Task | RTDL public | Idiomatic PyOptix | Strong PyOptix | Direct OptiX | Goal5847 RTDL control |
| --- | ---: | ---: | ---: | ---: | ---: |
| checked-U64 weighted triangle | 55.262 us | 86.632 us | 57.164 us | 47.115 us | 80.817 us |
| bounded AABB relation | 263.299 us | 2,500.272 us | 580.082 us | 245.410 us | 409.006 us |

Descriptive medians of implementation-entry and post-import intervals are not
the registered median-of-within-block-ratios estimator:

| Task | Arm | Entry to first correct result | Post-import to first correct result |
| --- | --- | ---: | ---: |
| triangle | RTDL | 934.486 ms | 776.201 ms |
| triangle | Strong PyOptix | 2,831.133 ms | 396.120 ms |
| relation | RTDL | 1,062.051 ms | 890.025 ms |
| relation | Strong PyOptix | 2,840.904 ms | 413.215 ms |

The lifecycle result is strongly affected by dependency-import and CUDA-context
placement and is not an intrinsic language speedup. Conversely, the old
post-import result remains roughly 2x adverse and is not hidden by the corrected
lifecycle endpoint.

The Direct gate is median-only. Triangle's per-block RTDL/Direct ratios were
`[1.452162, 1.164720, 1.175591, 1.147720, 1.394327, 1.401147,
1.168275, 1.160903]`; the two blocks above 1.35 are retained. Relation's were
`[1.069719, 1.080617, 1.061945, 1.109492, 1.113723, 1.091956,
1.063780, 1.069656]`.

## 7. Custody and independent verification

The successful archive is
`goal5848-ada89-rtx2000-c4351f612-transaction4-20260906.tar.gz`:

- archive bytes: 37,255,534;
- archive SHA-256:
  `f487f42580ac8cb81c202fe867b976ba7a267b9ca7ccffb980c626d775b112c8`;
- evidence-manifest seal:
  `4412d34597bbbef80dbfccf9367322d65cc060aab089010050335983aea298c8`;
- formal-transaction internal seal:
  `ea9728f4eba8cc6941f0bacc9a0da2c9f8e2ea84c8ac5426de803af9191064a5`;
- 2,405 manifest payloads totaling 125,733,693 uncompressed bytes;
- single-generation authority internal seal:
  `fb681997646ffed254e19ee2a3a2180f2676f8dc6e9d79ae0356ddd50f1911d8`;
- authority file SHA-256:
  `82bda443b3a21f5970e6f8e81fec34d57471c88e82a237ade8034bf93d4d1aed`;
- instrumentation authority seal:
  `94a94c9bf0ce688face25ee22e5604c7c1c175c5a9b5eba9f4c64ae976e36811`.

The 1,950-byte terminal transcript is retained separately with SHA-256
`d91483c38c1beabbc1cb774ec0587d32a463e69a9f6cf29891628140a369fef9`.

Independent checks performed after download:

1. the downloaded archive SHA exactly matched the pod-generated SHA file;
2. all 2,405 manifest rows matched exact path, byte count and SHA-256, and the
   enumerated file set had neither missing nor extra payloads;
3. all 2,446 tar members were safe regular-file/directory members, with no
   symlink, hard link, absolute path or parent traversal;
4. pod controller authority and pod independent recount were byte-identical;
5. a repository-external Mac diagnostic independently validated all 80 worker
   receipts and reproduced every task ratio and gate; its output SHA-256 is
   `51727572047483815fd38033082cc904112b5b4e1a54fc753a1bd1dd08681917`;
6. a live post-download pod check reconfirmed source `c4351f612...`, clean
   checkout, archive SHA and byte-identical authority files.

The full authority builder intentionally binds preregistered absolute pod paths
under `/workspace`. A direct Mac invocation therefore failed closed at path
resolution and was not called a portable full-authority replay. Worker-level
receipt and gate recount is relocation-safe and passed; full custody replay was
performed twice at the original pod layout and compared byte for byte.

## 8. Hostile self-review

### Attack: the system was tuned after seeing a near-threshold failure

This is true in the limited engineering sense: transaction 3 exposed a
`1.209372x` relation result, and v9 removed the measured redundant boundary.
It is not hidden as prospective evidence. The defense is procedural and
architectural, not statistical: transaction 3 is retained as failed; the
successor rule was preregistered; transaction 4 used wholly fresh processes;
and no threshold, estimator, workload, baseline, timer, sample count or adverse
row changed. Nevertheless, the optimization was informed by these two tasks,
so it is not evidence of arbitrary-workload performance.

### Attack: the lifecycle result is an import benchmark

Dependency import and CUDA-context placement materially favor RTDL at the
implementation-entry endpoint. The endpoint is valid for first usable result,
but it is not a language-only comparison. The old post-import ratios remain
mandatory and adverse, and any paper wording must present both boundaries.

### Attack: triangle is not uniformly within 1.35x of Direct

Correct. Two triangle block ratios are `1.452162x` and `1.401147x`. The frozen
Direct gate is median-only and passes at `1.171933x`; there is no authority for
a worst-block Direct bound or a statement that every execution is near Direct.

### Attack: the v9 ABI weakens cache validation

Source review and focused tests reject this. The digest is precomputed from the
same immutable packed input, supplied on every v9 fast call, required to be
exactly 32 bytes, and compared with the committed native digest while the
execution owner lock is held. The separate diagnostic query remains available.
Unknown or mismatched identity fails before cached execution.

### Attack: the authority is not relocation-portable

Correct for full custody reconstruction: preregistration binds absolute pod
paths. This is a disclosed artifact limitation. Two original-layout authority
builds are byte-identical, the complete archive is hash-bound, and the
relocation-safe worker/gate recount independently passes on the Mac. Do not
claim arbitrary-path full replay until the artifact layer explicitly supports
path rebasing.

### Attack: one Ada GPU and internal review are insufficient

Correct. This is why Goal5851 and later external review are hard gates. There is
no unresolved local P0/P1 against Goal5850's bounded acceptance criteria, but
there are unresolved blockers against Goal5848 completion and any public or
manuscript performance claim.

## 9. Acceptance audit

| Goal5850 criterion | Result |
| --- | --- |
| Exactly one idle supported RTX generation, exact detached clean source | PASS |
| One-shot preflight, AOT, cache, correctness, competence and instrumentation | PASS |
| Exactly 80 formal cells, zero retry/discard | PASS |
| Both tasks pass frozen correctness and performance gates | PASS |
| Authority and independent recount byte-identical | PASS |
| Output root, archive, SHA file and terminal transcript retained off checkout | PASS |

## 10. Claim boundary and next action

This report authorizes only the internal statement that Goal5850's first RTX
generation passed its frozen transaction. It does not authorize:

- a two-generation Goal5848 result;
- hardware-independent performance;
- an intrinsic RTDL-over-PyOptix or RTDL-over-Direct claim;
- omission of the adverse old post-import diagnostic;
- external consensus; or
- public/manuscript performance wording.

Goal5851 must use source commit `c4351f612...` unchanged on a GPU whose compute
capability generation differs from 8.9 and whose UUID differs from
`GPU-2fe387f0-ed74-e62c-0686-750461318361`. No documentation commit may replace
that exact experiment source identity.
