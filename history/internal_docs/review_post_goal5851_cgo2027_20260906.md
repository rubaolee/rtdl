# External review: RTDL CGO 2027 post-Goal5851 submission gate

Reviewer: Claude, acting as an independent external reviewer.

Review date: 2026-09-06

Target venue: CGO 2027. Deadline 2026-09-10. Source freeze 2026-09-08 00:00
America/New_York.

Prior review by the same reviewer:
`history/internal_docs/review_since_last_claude_goal5830_goal5848_20260905.md`.

## 1. Exact custody snapshot and files reviewed

Captured before any analysis, per Section 4 of the call for review:

```text
pwd                     /Users/rl2025/rtdl_v4_restricted_python_design
git rev-parse HEAD      04bd1d54f4641f12b6cf8e19a9e9eef5767a2021
git rev-parse HEAD^{tree}  06966bf16ea8ab1a2e8027543d8c00985c7389a6
git branch --show-current  codex/cgo-goal5836-handoff
git status --short      ?? history/internal_docs/independent_reaudit_cfr_claude_adjudication_20260906.md
                        (1 entry, untracked, excluded from this review as instructed)
```

Source-freeze boundary verified. `git diff --name-only d653fe4..HEAD` returns
exactly 11 paths, none under `src/`, `experiments/`, `tests/` or `scripts/`:

```text
AGENTS.md
history/internal_docs/call_for_review_post_goal5851_cgo2027_20260906.md
history/internal_docs/goal5850_generation_a_final_report_20260906.md
history/internal_docs/goal5851_cross_generation_final_report_20260906.md
history/internal_docs/goal5851_d653fe4_ampere_execution_packet_20260906.md
history/internal_docs/goal5851_second_generation_execution_packet_20260906.md
history/internal_docs/goal5851_triangle_exact_replay_repair_20260906.md
history/internal_docs/strict_self_review_since_last_claude_goal5848_goal5851_20260906.md
memory/decisions.md
memory/progress.md
memory/todo.md
```

I confirm the claim in Section 3 of the call: after `d653fe4`, only reports,
packets, policy and memory changed. The experiment source, native provider,
workloads, arms, timers, estimators, thresholds and tests are unchanged since
the measured commit.

**Reviewed directly:** the call for review; the strict self-review; the
2026-09-05 Claude review; the Goal5851 cross-generation final report; the
Goal5850 generation-A final report; `AGENTS.md`;
`KNOWN_STALE_CUSTODY_CHECKS.md`; `paper/cgo2027/main.tex` and its README;
`src/rtdsl/v4_rtdlexe.py`; `src/rtdsl/v4_family_schema.py`;
`src/rtdsl/v4_family.py`; `src/native/optix/rtdl_optix_core.cpp`;
`src/native/optix/rtdl_optix_v4_callback_poc.cpp`;
`experiments/goal5848_strong_baseline/{contracts,controller,worker,strong_pyoptix}.py`;
`scripts/goal5848_build_transaction_authority.py`;
`scripts/goal5840_independent_target_checker.py`; and the Goal5838 seal and
challenge-table authorities. Focused tests were executed; results in Section 9.

**Read-only compliance.** No source, evidence, authority, manuscript or
memory file was modified. The only file I created is this report. The stale
`.git/index.lock` from my previous review is gone; no new lock was created
(all Git commands used `--no-optional-locks`).

### 1.1 Scope notes on this review

**(a) The raw evidence was reachable, and was recounted.** The producing
machine's evidence folder was connected during this review at
`/Users/rl2025/rtdl_evidence`. I independently recounted both single-generation
transactions and the cross-generation authority from the raw 80-worker sample
vectors, not from any summary. Section 9 is a genuine independent recount and
may be cited as one. Everything the call for review asked me to reconstruct in
Section 7 reproduced exactly.

**(b) The pinned interpreter was not reachable.**
`/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python` is outside the connected
folder. All test results below used the workspace `python3` 3.10.12 with
`PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1`. Every suite I ran passed or
failed exactly as the self-review predicts, so I have no reason to think the
interpreter difference is material, but the project should reconfirm on 3.12.

### 1.2 First finding, recorded here because it is a custody defect in the packet itself

The call for review quotes the Ada archive digest as

```text
c9128bae15da7ed326c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced
```

which is **63 hexadecimal characters**. It is not a SHA-256. The Goal5851
cross-generation final report gives the correct 64-character value

```text
c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced
```

The packet dropped one `2`. I scanned every 40-to-80 character hex token in
both documents; this is the only malformed digest in either, and the only CFR
digest that disagrees with the report. Per the required trust order the report
wins. Recorded as P3-1: a reviewer who verified the archive against the
packet's own digest would have been unable to, which is exactly the failure
mode digests exist to prevent.

## 2. Cold-start restatement

**Problem.** A repurposed OptiX computation is a protocol, not a kernel. One
logical result is produced by host setup, geometry and buffer construction,
ray generation, intersection or built-in intersection, any-hit/closest-hit/miss
callbacks, payload and attribute conventions, continuation and reduction,
status and overflow handling, and a specific native executable. Each fragment
can be individually legal to CUDA, to OptiX and to the host language while the
assembled protocol is incoherent, incomplete or wrongly bound, and no existing
tool takes the assembled protocol as its input.

**Contribution as the authors now frame it.** Make the complete cross-role
callback protocol the compilation and admission unit. Callback source is parsed
as data, never imported; it becomes typed role-indexed Callback IR; effects,
cross-role semantic ABI ownership, physical binding, status-gated continuation
and completeness, and executable identity are discharged as one obligation set;
admitted protocols lower through compiler-owned trusted OptiX wrappers; output
publishes only through a checked lifecycle.

Critically — and this is the single largest change since my last review — the
project now states the boundary itself: *admission, canonical planning,
identity, provider binding and lifecycle are schema-parametric; executable
lowering remains compiler-owned and topology-specific.* Section 2 of the call
instructs reviewers not to award or reject the paper on a topology-generic
lowering claim the authors no longer make. I accept that framing. It is the
accurate description of the system and it is what I asked for on 2026-09-05.

**Non-claims.** No arbitrary Python compilation, no coverage of all OptiX
protocols, no automatic RT mapping, no application correctness, no soundness
theorem, no external human usability evidence, no real-world protocol-defect
prevalence.

**Deadline reality.** Four days to the deadline, under two to source freeze.
The manuscript has not been touched since 2026-08-31 and contains none of
Goals 5830–5851. That, not the evidence, is the binding constraint.

**Strongest current evidence.** Two same-source generations (RTX 4090 Ada CC
8.9, RTX 3090 Ampere CC 8.6) of a five-arm, same-contract experiment with a
genuinely strong Arm C, zero retry and zero discard, in which the public
checked RTDL path lands at 1.077x–1.175x of a purpose-built Direct CUDA/OptiX
route on prepared steady execution. If it recounts, that is a real and
publishable systems result.

**Largest open threat.** The metric that decides PASS was moved, after an
adverse observation, to an endpoint that includes each arm's dependency import
— the same confound the project itself correctly disqualified in Goal5847.

## 3. Closure of the 2026-09-05 review findings

| Prior finding | My current disposition | Basis |
| --- | --- | --- |
| **P0-1** sealed Goal5838 core performs no lowering; generality mislabeled | **Closed as a framing fix.** The project adopted "schema-parametric admission/identity/lifecycle with topology-specific trusted lowerers" and instructs reviewers not to evaluate a topology-generic lowering claim. Source is unchanged and my finding stands as a fact; the claim no longer overstates it. Remaining risk is that the manuscript still contains the old framing (P0-1 below) | Call §2; self-review §5; `v4_family_schema.py:1461-1467` still returns `"executable": false` |
| **P0-2** challenge domain is author-defined and narrow | **Open, correctly acknowledged, adequately handled.** The project accepts it and will preserve the exact ten-row domain wording and forbid "unbiased new-application sample." I re-verified the table: three topologies sharing role set `{make_ray, any_hit, miss, finalize}`, all `count_relation: query_count`, four already-supported primitives | `CHALLENGE_TABLE.json`; self-review §5 |
| **P0-3** Goal5845's 9.53x causal explanation contradicted by source | **Closed additively.** `CAUSAL_WORDING_CORRECTION_20260905.md` separates device deduplication from native-host final canonicalization; the weak-arm reciprocal is not paper-facing. Correcting additively rather than by rewriting the sealed report is the right custody choice | self-review §5 |
| **P1-1** Goal5838/5832 current-tree custody checks fail, undisclosed | **Partially closed.** `KNOWN_STALE_CUSTODY_CHECKS.md` now exists and is well written, covering Goal5838, Goal5840 and Goal5832. It omits Goal5837 and Goal5843, both of which I reproduced as failing today | See P2-1 |
| **P1-2** near-parallel exclusion absent on the Boolean route | **Closed by narrowing.** Claim restricted to the fixture domain by construction; no general closed-capsule correctness claim allowed. Runtime unrepaired, which I continue to regard as the correct deadline trade | self-review §5 |
| **P1-3** native/raw evidence bytes outside Git | **Improved, not closed.** Goal5848 archives now carry their exact native, Direct, PyOptix, PTX, CUBIN and receipts. Goal5838/5840 off-Git limits persist, and the Goal5848 archives are themselves outside Git | Call §6 |
| **P1-4** manuscript stale | **Open and materially worse.** `main.tex` last touched 2026-08-31; every line I cited on 2026-09-05 is still present verbatim | P0-1 below |
| **P2-1** provider identity is load-time image identity | **Closed by scope acceptance.** Do not imply per-call filesystem rehashing | self-review §5 |
| **P2-2** app-vocabulary blacklist is narrow | **Closed as hygiene.** Not to be used as architectural app-neutrality proof | self-review §5 |
| **P2-3** legacy app vocabulary in the package | **Open, artifact partitioning** | self-review §5 |
| **P2-4** README dead links; CFR misstated packaging | **Closed.** Links resolve; the packaging misstatement is acknowledged. Offline build dependencies still need disclosure | self-review §5 |
| **P3-1** Goal5848 instrumentation asymmetry | **Closed before formal data.** One explicit policy, paired ON/OFF protocol on both RTDL and PyOptix paths, 512 instrumentation workers per generation. I re-read `worker.py`: both arms now use `_measure_if(..., enabled=phase_instrumentation)`. This was fixed properly rather than argued away | `worker.py:425-437, 773-796` |
| **P3-2** pod endpoints in sealed evidence | **Open, correctly bounded.** Scrub a derived anonymous view; never mutate sealed authorities | self-review §5 |
| Goal5848 had 0/2 generations | **Closed internally.** Identical `d653fe4` passes Ada and Ampere | Section 9 |

Ten of thirteen prior findings are closed or correctly bounded. The project
did not argue with any of them and did not resolve any by choosing the more
favorable document. That is the strongest signal in this review.

## 4. New and reconfirmed findings

### P0-1 — Manuscript is untouched and now four days from deadline
*Manuscript overclaim / submission blocker.*

`git log -1 -- paper/cgo2027/main.tex` returns `d0bb93817`, 2026-08-31.
`paper/cgo2027/README.md` is the same commit. Every stale line from my previous
review is present verbatim:

| Line | Text | Truth |
| ---: | --- | --- |
| 673 | "prospective frozen-core extension exams remain zero" | one, at bounded scope |
| 1115 | "report a prospective unbiased new-application exam count of zero" | same, and "unbiased" is now forbidden wording |
| 935 | "Leaf primitives ... RTDL coverage & 2 / 4" | 4/4 kind presence |
| 50, 128, 156 | "two fixed protocol constructors" | needs the Goal5837 successor and Goal5838 instantiation beside it |
| 1183 | "1.36--2.83x faster than both Python-host arms at steady state" (Direct) | superseded by two generations of `d653fe4` data on different hardware |

The manuscript also has no RTX 4090 or RTX 3090 row, no five-arm description,
no dual-endpoint discussion, and no statement of the schema-parametric /
topology-specific boundary that Section 2 of the call now makes central.

This is the submission blocker. Everything else in this review is a paragraph;
this is the paper. With freeze on 09-08 the evaluation and claims rewrite must
start immediately and cannot be sequenced after further engineering.

### P0-2 — The gating endpoint was moved, after an adverse result, to one that includes each arm's dependency import
*Experiment-design limitation with manuscript consequences. This is my most serious new finding.*

From source, `experiments/goal5848_strong_baseline/worker.py`:

```python
# line 542
"implementation_entry_to_first_correct_result_ns": implementation_endpoint_ns
# derived at line 217-224 from implementation_start_ns = imported_started
```

`imported_started` is stamped **before** each arm's imports. For the strong
arm (lines 815-825) the timed prefix is:

```python
imported_started = time.perf_counter_ns()
from experiments.goal5802_premeasurement import pyoptix_scalar_arm as old_arm
baseline, preload_receipt = old_arm.preload_pyoptix_runtime()   # CuPy/PyOptix
from .strong_pyoptix import StrongPyOptixAdapter
import_ns = time.perf_counter_ns() - imported_started
```

For the RTDL arm (lines 357-361) it is two lightweight `rtdsl` imports.

So the primary endpoint now includes `preload_pyoptix_runtime()`. The project's
own `AGENTS.md` records that import at **5.206 s median** and states that it
"dominates the complete-process result" — which is exactly why Goal5847's
favorable `0.229370x` complete-process number was correctly refused as a
language-speed claim. The new primary endpoint is structurally the same
measurement, less extreme.

And it is the *gating* one. From `contracts.py:1288-1298`,
`all_performance_gates_pass` is built from implementation-entry median and
worst block, strong competence, public/Direct median, and
successor/predecessor. The post-import ratio is computed at lines 1275-1279 as
`post_import_diagnostic_reference_pass` and is **not** a term in
`all_performance_gates_pass`. Post-import is 1.559788x–1.837415x, i.e. it
fails the same 1.20x/1.35x limits, and that failure does not block the gate.

I want to be exact about what is and is not wrong here:

- **Not wrong:** the diagnosis. The old post-import endpoint genuinely was
  unfair to RTDL — pinned PyOptix had created CUDA state during its excluded
  import while RTDL stayed lazy and paid CUDA initialization inside its timer.
  `AGENTS.md:108-112` states this plainly and even warns against moving RTDL
  initialization into import to manufacture a pass. That restraint is real.
- **Not wrong:** the custody. Both endpoints are computed with identical
  thresholds, both are retained, the adverse one is mandatory and visible, and
  the status string embeds `LIFECYCLE_CORRECTED`.
- **Wrong:** the remedy. The correct repair for "the baseline pre-warms CUDA
  during the excluded region" is to *equalize pre-endpoint state* — require
  both arms to hold an initialized CUDA context at `endpoint_start`, or
  neither. Moving the boundary outward instead replaces a moderate asymmetry
  that disfavored RTDL with a larger one that favors it, and makes the pass
  decision rest substantially on dependency-packaging weight rather than on
  compiler or runtime cost.

**Measured confirmation from the raw evidence.** I decomposed every formal
worker's `implementation_import_ns`, `post_import_to_first_correct_result_ns`
and `implementation_entry_to_first_correct_result_ns`, taking the median over
the eight blocks (all values in ms):

| Generation | Task | arm | import | post-import | entry | import as % of entry |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Ada | Triangle | A RTDL | 76.9 | 449.4 | 526.0 | 14.6% |
| Ada | Triangle | C strong | 529.6 | 287.4 | 817.5 | **64.8%** |
| Ada | Relation | A RTDL | 77.5 | 455.2 | 532.0 | 14.6% |
| Ada | Relation | C strong | 577.8 | 261.4 | 842.0 | **68.6%** |
| Ampere | Triangle | A RTDL | 80.1 | 370.7 | 451.9 | 17.7% |
| Ampere | Triangle | C strong | 502.8 | 226.5 | 729.1 | **69.0%** |
| Ampere | Relation | A RTDL | 81.2 | 379.4 | 460.5 | 17.6% |
| Ampere | Relation | C strong | 467.0 | 206.3 | 673.4 | **69.4%** |

Arm C carries 386–500 ms more import than Arm A on every row, 5.8x to 7.5x
more. Import is 65%–69% of Arm C's entire measured entry endpoint, against
15%–18% of Arm A's. The import term alone flips the direction: on post-import
RTDL is 1.56x–1.84x slower, on entry it is 0.62x–0.68x faster, and nothing
else in the decomposition changes sign.

The dispersion tells the same story. Across the eight blocks the RTDL/Direct
steady ratio varies by 1.4%–3.1% around its median, while the entry A/C ratio
on Ampere relation ranges from its 0.681393x median up to 0.911861x — a 34%
spread. The steady metric is stable because it measures compute; the entry
metric is noisy because it substantially measures module loading.

Neither endpoint measures what a CGO reader will think "first result" measures.
One is deflated by the baseline's eager CUDA init outside the timer; the other
is inflated by the baseline's dependency import inside it. The bracket
[0.618x, 1.837x] is honest; either endpoint alone is not.

**Required disposition.** Not a reason to re-run and not a reason to withhold
the paper. It is a binding constraint on presentation:

1. The headline performance result must be the **prepared steady public
   RTDL/Direct** comparison (1.077x–1.175x). It has no import confound, the
   arms hold equivalent state, and validation is outside the timer on every arm.
2. First-result performance, if it appears at all, must appear as **both**
   endpoints together, with one sentence naming the confound in each direction.
3. The implementation-entry ratio may never be described as a speedup, as
   parity, or as a language or compiler property, and may not be combined with
   any steady ratio in one causal statement.

If the paper does 1–3, this finding is fully discharged. If the paper leads
with 0.62x, I would consider that fatal at review.

### P1-1 — Provider bind/close double-fault: confirmed, correctly characterized, and descopeable
*Source/runtime defect.*

I read `src/rtdsl/v4_rtdlexe.py:3078-3121` directly and confirm the
self-review's account.

In `bind()`'s handler:

```python
except BaseException:
    if library is not None:
        try:
            _release_native_library_image(library)
        finally:
            if readiness is not None:
                readiness.close()
    elif readiness is not None:
        readiness.close()
    with self._lock:                       # <-- never reached if release throws
        self._library = None
        self._readiness = None
        if self._state not in {"BOUND", "CLOSED"}:
            self._state = "CLOSED"
    raise                                  # <-- never reached either
```

If `_release_native_library_image` raises, the secondary exception propagates
out of the `try/finally`, the explicit `raise` never executes, and the state
block is skipped: `_state` remains `BINDING` and the references stay set.

In `close()` the object is marked terminal **before** release is attempted:

```python
with self._lock:
    if self._state in {"BOUND", "CLOSED"}: return
    library = self._library; readiness = self._readiness
    self._library = None; self._readiness = None
    self._state = "CLOSED"        # <-- set before release can fail
if library is not None:
    try:
        _release_native_library_image(library)   # <-- may fail again
    finally: ...
```

so a second release failure leaves a `CLOSED` object with dropped references
and no retry handle, and a third `close()` returns immediately at the guard.
This matches the self-review's fault-injection trace exactly.

**My independent severity judgment, which differs from treating this as a
central-claim threat.** The paper's central failure claim is *status-gated
publication*: no output escapes a failed status. This defect is on the
asynchronous provider-initialization path, requires a secondary failure during
cleanup of a primary failure, and ends with `bind()` raising — no provider is
returned, so no execution and no output occurs. It cannot produce a wrong
result and cannot have affected any formal sample; it is outside every timer.
What it refutes is only a broad statement that *every* provider failure path
preserves the primary exception and retains retryable ownership. The project
should simply not make that statement.

**Recommendation: descope and disclose; do not repair before freeze.** The
repair is small — wrap the release in `try/except`, re-raise the original in an
outer `finally`, and set `CLOSED` only after release succeeds — but any repair
changes source identity away from `d653fe4`, and `d653fe4` is what the two
generations measured. Trading the identity of the entire performance evidence
for a defect that cannot affect a result or a sample is a bad trade two days
before freeze.

If the project repairs anyway, the honest disclosure is: the performance
evidence is evidence for `d653fe4`; the submitted source is `d653fe4` plus one
named cleanup patch confined to a failure path outside all timers; and the
patch is listed in the artifact with its diff.

### P1-2 — Repeated result-informed repair on two fixed workloads
*Experiment-design limitation.*

Goals 5842 → 5843 → 5844 → 5845 → 5846 → 5847 → 5848 → 5850 → 5851 form a
long measure-repair-remeasure loop on the same two tasks. The final
transactions are therefore **not confirmatory**. They are a fresh
engineering-gate validation of an implementation that was tuned against these
two workloads, on hardware that changed between rounds.

What legitimately constrains the concern: workloads, arms, timers, estimators
and thresholds were frozen and unchanged between generations; every adverse
predecessor archive is retained and unpooled, including the `a4dd1d5d` Ampere
pass / Ada failure pair; zero retry and zero discard; and the same source ran
on two generations. That is a good deal stronger than typical.

What it does not license: describing the result as confirmatory, generalizing
to unmeasured workloads, or implying the overhead figure would hold for a task
that was never in the tuning loop. The paper must say "two frozen tasks, tuned
against these tasks, validated under frozen gates on two GPU generations."

### P1-3 — The regression control is steady-only, and the successor is adverse against its own predecessor on both first-result endpoints
*Experiment-design limitation. Found in the recount; not raised by the self-review or the call.*

The successor/predecessor gate exists to prevent buying first-result parity by
regressing the previously fast prepared path. It is registered on steady
execution only (`contracts.py:1263-1266, 1296-1297`). I computed the same
median-of-within-block-ratios for Arm A against the frozen predecessor Arm E on
all three endpoints:

| Generation | Task | steady (gated) | post-import | entry |
| --- | --- | ---: | ---: | ---: |
| Ada | Triangle | 0.9030x | 1.1693x | 1.0796x |
| Ada | Relation | 0.5844x | 1.3054x | 1.1924x |
| Ampere | Triangle | 0.9224x | 1.1628x | 1.1376x |
| Ampere | Relation | 0.6082x | 1.2617x | **1.2167x** |

The successor is faster than its predecessor at steady state on every row, and
**slower on every row at both first-result endpoints** — by 16%–31% at
post-import and 8%–22% at entry. The Ampere relation entry ratio of 1.2167x
would fail a 1.20x limit if the regression gate applied to the endpoint the
project made primary.

This is not a gate violation: the gate is registered on steady and passes
honestly. It is a blind spot. The control that the paper will cite as its
defence against endpoint gaming does not cover the endpoint that became
primary, and on that endpoint the successor regressed. Combined with P0-2, the
picture is consistent and should be stated plainly: the favorable entry ratio
comes from the baseline's import weight, not from the successor improving
first-result behaviour — the successor made first result *worse* than its own
predecessor while making steady execution substantially better.

**Disposition.** No re-run required. The paper must not present the
successor/predecessor control as evidence about first-result behaviour, and if
first-result numbers appear at all, the predecessor comparison on those
endpoints should appear with them.

### P2-1 — The custody guide omits two of the four failing historical checks
*Artifact usability problem.*

`KNOWN_STALE_CUSTODY_CHECKS.md` documents Goal5838, Goal5840 and Goal5832. I
reproduced all four disclosed failures on the current tree:

```text
tests.goal5838_core_seal_and_selection_test   FAILED (errors=1)
  Goal5838SealError: sealed file drift: src/rtdsl/v4_family_schema.py
tests.goal5832_protocol_shape_algebra_test    FAILED (errors=1)
  AlgebraError: goal5831.source_authorities[1] byte count drift
scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored
  Goal5837Error: AUTHORITY_CURRENT_INPUT_MISMATCH
scripts/goal5843_build_final_authority.py --verify-stored
  Goal5843ContractError: preregistration differs from canonical builder
```

Goal5837 and Goal5843 are absent from the guide. This confirms self-review
finding 6. An artifact evaluator running the documented commands will hit two
undocumented red results. One hour to fix, and it protects the artifact badge.

### P2-2 — Lazy receipt validation is correctly bounded, with one family asymmetry
*Verified favorably; one wording limit and one small observation.*

I traced the deferred path in `_DeferredCompactDeviceStatus`
(`v4_rtdlexe.py:5388-5440`). The publication gates are sound:

- `compact_status != 0` triggers full synchronous validation, materializing the
  receipt, followed by `raise AssertionError("unreachable compact-status
  failure")` so a failing status cannot fall through;
- for `family == _BOUNDED`, **all** structural relations (raw/unique counts,
  overflow, semantic and raw capacities) are validated synchronously on the
  success path using fixed-size integer checks that deliberately do not
  materialize the receipt;
- `_raise_native` (line 3989) is a no-op at status 0, so `d653fe4`'s
  `if native_status:` guard is semantics-preserving;
- the `"ok"` fast path returns `True` only for instances whose constructor
  already proved `compact_status == 0`.

Answering call question 8.12 directly: **lazy receipt validation does not
create a semantic publication gap.** What is deferred is measurement
bookkeeping — D2H bytes, prepared-input reuse, monitor fields — after
synchronous native status, synchronous compact status and the output oracle.

Two limits. The required wording limit stands: the paper must not claim every
measurement receipt field is eagerly expanded and validated before ordinary
scalar output is observable. And the synchronous structural block is guarded by
`if family == _BOUNDED`, so the triangle family relies on compact status plus
the exact U64 oracle rather than an equivalent structural check. That is
adequate for a scalar with an exact expected value, but the strength of the
synchronous gate differs by family and the paper should not describe it
uniformly.

### P2-3 — Full-repository discovery is not a usable artifact gate
*Artifact usability problem.*

The self-review reports 13,638 tests with 756 failures, 6,214 errors and 600
skips. I did not re-run it; the call explicitly warns against broad discovery
and I accept the number as reported. My judgment on call question 8.21: this is
**not** a submission blocker, because it mixes absent historical assets,
optional platforms and current tests, and because CGO artifact evaluation asks
for a documented reproduction path, not a green monorepo. It **is** an artifact
blocker in the sense that the artifact must ship a layered test matrix naming
which suites are expected green (the `goal5848*` and `goal5851*` suites), which
are expected red and why (the four historical custody checks), and which
require absent hardware or assets. Anything less invites an evaluator to run
discovery and conclude the artifact is broken.

### P3-1 — Malformed archive digest in the review packet

See Section 1.2. Documentation/custody hygiene.

### P3-2 — Ampere launcher invocation error

The first Ampere invocation failed closed at `validate_exact_git_checkout`
before creating an output root, preparing dependencies or running any worker.
No samples or evidence rows existed to pool. Disclosing it is correct and
calling it an invocation error rather than a transaction failure is accurate. I
raise it only to confirm that I checked the distinction and agree with it.

## 5. Architecture and generality verdict

Answering call questions 8.1–8.4.

**8.1 — Is "bounded whole-protocol compiler" accurate?** Yes, with the
qualifier the project now supplies. The system takes the complete cross-role
protocol as its admission unit, discharges five obligations over it as one set,
and binds identity through execution. That the executable lowerers are
topology-specific narrows the claim; it does not disqualify the word compiler.
A compiler with a fixed set of hand-written back ends is still a compiler. The
accurate phrase is the project's own: *schema-parametric admission, planning,
identity, provider binding and lifecycle, with compiler-owned topology-specific
lowerers.*

**8.2 — Is this a CGO contribution, or library engineering?** A CGO
contribution, and I say this having been the reviewer who last time counted the
2,635 hand-written post-selection lines. The reason is that the novelty is not
in the lowerers. It is in making the protocol the admission unit and showing
that admission, canonical planning, identity and lifecycle can be made
parametric over protocol shape while lowering stays trusted and specific. That
is a real architectural claim about where a compilation boundary should sit,
it is falsifiable, and Goal5838 falsifiably tested one instance of it. Library
engineering would be the same set of routes with no shared obligation
machinery and no parametric admission; that is not what the source shows.

The honest cost, which the paper must state: the topology-specific trusted code
is large relative to the parametric core, so the contribution is an
architecture and an obligation system, not a code-generation advance.

**8.3 — Is "one prospective compositional-extension result over a frozen
author-defined ten-row domain" too strong?** No — that wording is exactly
right, and it is a marked improvement over the previous framing. I re-verified
its components: the seal predates selection; the table was frozen with a
recorded digest; the selection client was committed with its own digest; the
target pulse was in the future when the protocol was committed; pre-selection
activity records zero candidate executions and zero candidate-specific provider
implementations. Two further words remain mandatory in any sentence using it:
*compositional* (the selected row recombines an already-supported primitive
with an already-supported topology) and *author-defined* (all three topologies
share one role set and one count relation). With those, the sentence is
defensible. Without them it is not.

**8.4 — Which sentences must avoid "generic," "arbitrary," "unbiased"?** All of
them, in these positions specifically: any sentence about lowering or code
generation ("generic lowering", "generic compiler back end"); any sentence
about the Callback IR's execution reach ("arbitrary Callback IR", "arbitrary
restricted-Python callbacks"); any sentence about the Goal5838 selection
("unbiased exam", "unbiased new-application sample", "blind exam"); and any
sentence about the owner-grouped or relation continuation as a system property
("generic continuation" is acceptable only as "application-neutral bounded
continuation available to any protocol on that route"). "Generic" is safe in
exactly one place: describing the admission, identity and lifecycle framework
as schema-parametric.

## 6. Goal5838 bounded prospective-exam verdict

Unchanged in substance from 2026-09-05, and now correctly labeled.

The result establishes: at commit `7da6805`, a protocol shape selected by a
NIST beacon pulse from a frozen ten-row table was admitted, lowered, executed
in two true OptiX launches on RTX 2000 Ada under OptiX 9, and matched twelve
independent rational-oracle rows, without modifying the three sealed files
implementing schema admission, provider projection, executable identity and the
public lifecycle.

It does not establish: topology-generic lowering (the sealed core's
`lower_canonical_compilation_plan` returns a document with `"executable":
false`); an unbiased or representative sample (the domain is 4 already-supported
primitives × 3 any-hit variants sharing one role set and one `query_count`
result relation); or anything about the current tree, where the seal verifier
fails by design after Goals 5844/5846/5847 legitimately modified sealed files.

Two conditions on use. The result must be stated in the past tense bound to
`7da6805`. And the ~2,635 lines of post-selection topology-specific code should
be stated as a cost of the extension, not omitted — a reader who discovers it
independently will discount everything else in the section.

One residual I raised before and still cannot resolve from the table:
`builtin_round_linear_curve::any_hit_terminate_bool_per_query` is an eligible
row, but Goal5834-B3 delivered a per-query Boolean curve route before Goal5838.
If that row was already implemented, the eligible denominator is nine, not ten.
The project should check and state the answer rather than let a reviewer find it.

## 7. Goal5840 independent-checker verdict

Answering call questions 8.5–8.7.

**8.5 — Is "independent finite structural check over specialized target
output" correct?** Yes, and it is the right level of modesty. I confirm
independence from source:
`scripts/goal5840_independent_target_checker.py` imports only `argparse`,
`ast`, `base64`, `hashlib`, `json`, `re`, `pathlib` and `typing`. It never
imports `rtdsl`; the only `rtdsl` strings are file paths it reads and parses.
It refuses to consume compiler-produced projections at all
(`TC000_COMPILER_PROJECTION_FORBIDDEN`).

I will add one point in the project's favor that the label undersells: the
checker is not only structural. `TC001_PARTIAL_EVAL_*` partially evaluates the
generated device source against expected `make_ray`, `intersection`,
`any_hit`, `accept_continue` and `finalize` semantics, and `TC001_*_SYMBOL_*`
requires each role symbol to agree simultaneously across compiled ABI metadata,
wrapper source and compiled PTX. "Finite structural check" is defensible and
slightly modest; "general partial evaluation" would be an overclaim. Either
way, the honest scope is three route groups, four modes, five properties.

**8.6 — Does the unconditional-early-return probe require stronger wording, or
invalidate a claim?** It requires a limitation sentence and invalidates
nothing currently intended. The checker verifies a finite set of declared
properties over specific named functions in three named routes; it does not
verify general control-flow equivalence or numerical semantics. A mutation that
the property set does not name can pass. The paper must therefore say the
denominator explicitly and must not phrase the result as "the checker validates
the lowering." It validates five declared properties of three lowerings.

**8.7 — Does independence from `rtdsl` materially reduce circularity despite
shared source-layout assumptions?** Yes, materially, though not completely. It
eliminates the strongest circularity — a verifier that re-derives its answer
through the same code — and the refusal of compiler projections eliminates the
second strongest. What remains is that the checker hard-codes route ids and
function names (`route_id.startswith("stable::bounded_relation")`,
`PreparedBoundedRelationOwner.execute`,
`verify_precanonical_bounded_relation`), so it shares the implementation's
structural assumptions and a legitimate refactor breaks it without any semantic
change. That is a maintenance and generality limitation, not circularity.

## 8. Baseline fairness and same-contract verdict

Answering call questions 8.8–8.13, per arm.

**Arm A, public RTDL.** Same contract. Steady samples come from the public
prepared-replay path with synchronous native status, synchronous compact
status, and the exact output oracle. Not a native kernel-only path — answering
8.10 affirmatively.

**Arm B, idiomatic pinned PyOptix.** Same semantic contract, weaker
implementation by design. Its role is to establish that Arm C is not a
strawman, via the `C/B <= 1.05x` competence gate
(`contracts.py:1293`, `STRONG_COMPETENCE_RATIO_LIMIT_PPM = 1_050_000`).

**Arm C, strong PyOptix.** Genuinely strong, and this is the decisive
improvement over Goal5845. `strong_pyoptix.py:100-112` loads a
`goal5802_relation_unique_compact` CUBIN as a CuPy `RawModule` and binds it as
a device compaction kernel, giving the baseline the same device-side
deduplication RTDL performs; and `_make_validation_off_context` gives it the
fast OptiX configuration. I found no unmatched RTDL-favorable work placement in
the prepared region — answering 8.9 affirmatively. The one asymmetry I flagged
in the previous review, instrumentation gating, is fixed.

**Arm D, Direct CUDA/OptiX.** Purpose-built lower bound under a matched output
contract. This is the arm the headline claim should rest on.

**Arm E, predecessor RTDL.** Regression control at `<= 1.05x`
(`SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM`). Observed 0.584x–0.922x, so the
successor is faster on every row — the control is satisfied with margin, which
is the specific defence against buying first-result parity by regressing the
prepared path.

**Timer symmetry, answering 8.8.** Verified in source. `_sample`
(`worker.py:168-186`) warms up with validation, then times `action()` alone and
validates *after* the timer stops, identically for every arm. Output validation
cost is therefore excluded from steady samples uniformly. Both first-result
endpoints are computed from the same stamps on every arm. The endpoint
*selection* problem in P0-2 is about which boundary is primary, not about
asymmetric application of a boundary.

**8.13 — Is the 1.20x public/Direct median gate reasonable without a
worst-block gate?** Yes, and the data make the omission immaterial. From
`contracts.py:1294-1296` the public/Direct term is median-only; there is no
`max(public_direct)` term. But the reported dispersion is tight — medians
1.076852x–1.175066x against observed maxima 1.092253x–1.211025x, so the worst
block exceeds the median by 1.4%–3.1% and every block sits below the median
gate's own neighbourhood. Retaining and reporting every block is sufficient
here. Three cautions: the `1.35x` limit belongs to the implementation-entry
RTDL/strong comparison and must never be borrowed for Direct (the Goal5850 and
Goal5851 reports carry explicit corrections for exactly this, and I verified
`AGENTS.md:116` attributes 1.20x/1.35x to the first-result endpoint, so
finding 8 of the self-review is discharged in current prose); the median gate
must not be converted into a tail bound; and "within 1.20x of Direct on the
median" is a *no-unacceptable-median-tax* statement, never a speedup.

## 9. Goal5848/Goal5851 evidence recount and performance verdict

### 9.1 Source-level and test verification

**Gate logic, from source.** `contracts.py:1288-1298` composes
`all_performance_gates_pass` from: implementation-entry median
`<= 1_200_000` ppm and worst block `<= 1_350_000`; strong competence
`<= 1_050_000`; public/Direct median `<= 1_200_000`; successor/predecessor
`<= 1_050_000`. `post_import_diagnostic_reference_pass` is computed at lines
1275-1279 with the same limits and is deliberately excluded from the gate. The
gate raises `Goal5848ContractError` if any task fails, so a partial pass cannot
be reported as a pass. This matches the frozen contract as documented.

**Freeze integrity.** `d653fe4..HEAD` touches no source, experiment, test or
script (Section 1). The measured source is the shipped source.

**Focused suites**, on Python 3.10.12 with bytecode writing disabled:

```text
unittest discover -s tests -p 'goal5848*_test.py'        128 tests  OK
unittest discover -s tests -p 'goal5848*_test.py'  (-O)  128 tests  OK
tests.goal5851_triangle_fused_replay_test                  7 tests  OK
```

**Disclosed historical failures** reproduce exactly as predicted; see P2-1.

**`d653fe4` obligation preservation, answering 8.11.** I read the diff and
tested the one change that could have been a safety regression. The commit
replaces a live `os.getpid()` with a cached `_NATIVE_IMAGE_CACHE_PID` in the
process-boundary guard of both prepared owners (`v4_rtdlexe.py:5682, 6186`).
That would defeat the fork guard if the cache were stale in a child. It is not:
line 259-260 registers `os.register_at_fork(after_in_child=...)`, and the hook
(lines 240-256) resets `_NATIVE_IMAGE_CACHE_PID = os.getpid()`, replaces
inherited locks, nulls the inherited CUDA context state, and poisons the cache
if native runtime was touched. I confirmed behaviourally:

```text
parent _NATIVE_IMAGE_CACHE_PID: 4  os.getpid(): 4
child  os.getpid()=5  cache_pid=5  poisoned=False
```

so in a child `_NATIVE_IMAGE_CACHE_PID != self._pid` and `RX038_PROCESS_BOUNDARY`
fires exactly as before. The optimization is semantics-preserving and I credit
it. Thread, owner, close and non-reentrancy checks are untouched; native and
compact status remain synchronous; the U64 oracle remains checked before
return. Answering 8.11: **yes, `d653fe4` preserves the obligations and defers
only measurement bookkeeping.**

### 9.2 Independent recount of the raw evidence

The evidence folder was connected during this review. I recounted both
generations from the 80 raw worker JSON files per generation, recomputing every
median from the stored 128-sample vectors with the project's own
`integer_median` and `ratio_ppm` definitions (`contracts.py:795-802, 805-811`),
and never reading the authority's own `recount.tasks` summary.

**Digests.** All five verify:

```text
Ada archive      c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced  OK
Ampere archive   7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2  OK
Ada authority    191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7  OK
Ampere authority 35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3  OK
cross-generation 99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692  OK
```

`single-generation-authority.json` and `single-generation-authority.recount.json`
are byte-identical in both generations, as are the two cross-generation files.
The recomputed Ada archive digest also confirms that the call for review's
63-character value (P3-1) is a transcription error, not a different artifact.

**Structure.** Per generation: 80 worker files, 5 arms x 2 tasks x 8 blocks,
16 workers per arm, all `PASS__GOAL5848_WORKER`; 128 samples each for 10,240
retained samples; `retry_count: 0`, `discard_count: 0`; one GPU UUID per
generation with no mixing (`GPU-01a12a86-...` Ada, `GPU-eda7acdc-...` Ampere);
exactly two source commits present, `d653fe4...` for arms A–D and
`12ab1bc0a...` for the frozen predecessor arm E, which is the intended design.
`EVIDENCE_MANIFEST.json` reports `file_count: 2405` and `payload_bytes:
125718265` under seal `8cbd6091...` for Ada, matching the final report exactly.
Instrumentation authorities report `process_count: 512` and
`PASS__PAIRED_FRESH_PROCESS_INSTRUMENTATION_OVERHEAD_WITHIN_FIVE_PERCENT` on
both generations.

**Anti-fabrication check.** For all 160 workers across both generations, the
median I recomputed from the raw `samples_ns` vector equals the stored
`median_ns` exactly. Zero mismatches. A summary detached from its samples would
have shown here.

**Registered results, recomputed from raw samples:**

| Generation | Task | RTDL/Direct median | max block | entry A/C | post-import | successor/pred |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Ada | Triangle | 1.175066x | 1.211025x | 0.642180x | 1.559788x | 0.903016x |
| Ada | Relation | 1.076852x | 1.092253x | 0.653826x | 1.749327x | 0.584438x |
| Ampere | Triangle | 1.133636x | 1.142675x | 0.618362x | 1.637468x | 0.922388x |
| Ampere | Relation | 1.094795x | 1.118811x | 0.681393x | 1.837415x | 0.608228x |

**Every figure matches the committed Goal5851 report to the last digit.** Gate
directions recompute as registered: public/Direct median under 1.20x on all
four rows; entry median under 1.20x with worst block under 1.35x on all four;
competence and successor/predecessor under 1.05x on all four; and the
post-import diagnostic failing the same limits on all four, as it must.

**Cross-generation authority.** `cross_machine_raw_time_ratio_computed: false`,
`only_within_machine_registered_gates_compared: true`, `generation_count: 2`,
`retry_count: 0`, `discard_count: 0`, `public_or_manuscript_claim_authorized:
false`, `external_review_complete: false`. No raw time is compared across
machines.

**Adverse custody, spot-checked.** The evidence root retains the failure
archives the reports describe, unpooled and separately named, including
`goal5851_ada_a4dd1d5d_formal_failure_rtx4090`,
`goal5851_successor_ampere_a4dd1d5d_pass`, two Ada pre-formal failures, an
Ampere transaction-1 failure, and the earlier transaction-3 failure archive
with its own digest sidecar. The claim that no adverse archive was pooled with
the final source is consistent with what is on disk.

### 9.3 Three observations the recount adds

**(a) Arm B is very weak, which retroactively sizes an earlier finding.** The
competence gate requires `C/B <= 1.05x`; the measured values are 0.602851x and
0.654279x on triangle and **0.220775x / 0.226921x** on relation. The strong arm
is roughly 4.5x faster than the idiomatic arm on the relation task. The gate's
purpose — proving Arm C is not a strawman — is met with enormous margin, and
the number also quantifies my P0-3 from 2026-09-05: any comparison drawn
against the idiomatic arm, as Goal5845's withdrawn 9.53x was, overstates RTDL
by about that factor. Keeping Arm B in the paper is worthwhile precisely
because it makes this visible.

**(b) The most adverse single number in the dataset is not in the report.**
The post-import worst block on Ampere relation is **2.377129x**, against the
1.837415x median that the report gives. The reports publish post-import medians
only. Since the post-import result is mandatory retained adverse evidence, the
paper should give its range, not only its median.

**(c) The entry endpoint is the noisiest metric in the experiment.** See the
dispersion note in P0-2. This is corroborating evidence that it measures
loading rather than compute.

### 9.4 Performance verdict

**The evidence recounts, and it is the strongest artifact the project has.**
A public, fully checked, status-gated protocol path at 1.077x–1.175x of a
purpose-built Direct CUDA/OptiX implementation, same source across two GPU
generations, against a device-continuation baseline proven competent, with
zero retry, zero discard, 160 workers whose stored medians all reproduce from
their raw samples, byte-identical independent recounts, and no cross-machine
raw-time comparison. On the evidence I can now say this without the conditional
I attached before the folder was connected.

Three boundaries remain, unchanged by the recount: two frozen tasks tuned
against those tasks (P1-2); a median statement with no registered tail bound on
Direct (Section 8); and prepared steady execution only — not first result, not
cold start, not arbitrary workloads.

## 10. Endpoint and adaptivity verdict

Answering call questions 8.14–8.17.

**8.14 — Is changing the primary endpoint after observing the adverse
post-import state mismatch defensible?** Partially. The *diagnosis* is correct
and the *custody* is exemplary — identical thresholds, both endpoints computed,
the adverse one mandatory and visibly failing, a status string that says
`LIFECYCLE_CORRECTED`, and an explicit written prohibition on moving RTDL
initialization into import. But the chosen remedy does not remove the
asymmetry; it inverts and enlarges it, because the new endpoint contains the
baseline's ~5.2 s dependency import. As the *gating* metric it is not
defensible. As one half of a reported bracket it is. See P0-2.

**8.15 — Must the paper show both, and what causal wording is safe?** Yes, both,
always adjacent. Safe wording, verbatim:

> Measured from entry into each implementation, RTDL reaches a first validated
> exact result in less time than the strong PyOptix arm on both generations;
> measured from the end of each implementation's imports, it takes more. The
> first boundary includes each arm's dependency import and CUDA context
> placement; the second begins after the pinned baseline has already created
> CUDA state during its excluded import while RTDL initializes inside its
> timer. Neither boundary isolates language or compiler cost, and we do not
> use either as a speedup claim.

Unsafe, and forbidden: any sentence of the form "RTDL reaches first result
1.6x faster", any use of the implementation-entry ratio without the post-import
ratio in the same paragraph, and any combination of a first-result ratio with a
steady ratio in one causal statement.

**8.16 — Confirmatory, or fresh engineering-gate validation of a task-tuned
implementation?** The latter, unambiguously. See P1-2. The word "confirmatory"
must not appear.

**8.17 — Do frozen thresholds, workloads, arms, timers and estimators plus
adverse custody sufficiently constrain p-hacking?** For the bounded claim, yes,
with one exception. Freezing the contract before the run, running identical
source on two generations, retaining every adverse archive unpooled, and
enforcing zero retry and zero discard together constrain the usual degrees of
freedom well. The exception is precisely the endpoint: the thresholds were
frozen, but *which comparison the thresholds gate* was changed after an adverse
observation. That is the one remaining researcher degree of freedom, it is
disclosed, and P0-2's presentation rules are how to neutralize it.

## 11. Provider double-fault and failure-semantics verdict

Answering call questions 8.22–8.24.

**8.22 — Reproduced, and does it contradict a central claim?** Confirmed from
source at `v4_rtdlexe.py:3078-3121`; mechanism in P1-1. It does **not**
contradict the central status-gated-publication claim: `bind()` still fails, no
provider is returned, no execution occurs, no output publishes, and no timed
path is involved. It contradicts only a broad "every provider failure preserves
the primary exception and retains retryable ownership" claim.

**8.23 — Can the paper descope it while keeping status-before-output and
ordinary cleanup claims?** Yes. Keep: status precedes output on every path;
ordinary single-fault cleanup releases the native image and readiness lease and
re-raises the original exception. Descope: any universal statement about
double-fault paths. Disclose: a named limitation that a secondary failure
during cleanup of a primary bind failure can mask the primary exception and
leave the capability without a retry handle, that it is outside all timed
paths, and that it cannot affect a published result.

**8.24 — If repaired, can the existing evidence still be used?** Yes, with
explicit disclosure. The two-generation evidence is evidence for `d653fe4`. If
the repair lands, the paper must state that the submitted source is `d653fe4`
plus one named patch, that the patch is confined to the asynchronous
provider-initialization failure path outside every timed region, and that no
performance number was re-measured. The artifact should carry the diff.

**My recommendation: do not repair before freeze.** The defect cannot affect a
result or a sample; a repair costs the source identity of the entire
performance chain two days before freeze. Disclosure is the better trade. If
the project repairs anyway for engineering reasons, the disclosure above makes
it survivable.

## 12. Artifact, custody and replay verdict

Answering call questions 8.18–8.21.

**8.18** — Performed; see Section 9.2. Both single-generation authorities and the cross-generation gate direction reconstruct exactly, with no missing, pooled, retried, discarded or inconsistently sourced rows. The only sourcing split is the intended one: arms A-D at `d653fe4`, predecessor arm E at `12ab1bc0a`.

**8.19 — Is the absolute-path authority limitation acceptable?** Yes, if stated
the way the project already states it internally: the full authority binds
pod-absolute `/workspace` paths and does not rebuild unchanged after
relocation; the portable manifest and the worker/gate recounts do pass after
relocation. That is an honest and unusual disclosure. The artifact wording must
make the distinction in the artifact README itself, not only in an internal
report, because an evaluator who runs the full-authority rebuild after
downloading will otherwise see a failure and stop. Name the two recounts that
*are* portable and give their commands.

**8.20 — Are the historical custody boundaries separable from current-source
testing?** Yes in principle and nearly so in practice. The four failing checks
are all snapshot-drift artifacts of authorities deliberately bound to old
commits, none is a current runtime defect, and the guide's replay-at-the-bound-
commit recipe is the right pattern. The gap is coverage: two of the four are
undocumented (P2-1).

**8.21 — Does full-repository discovery require a submission blocker?** No — a
layered artifact test matrix is adequate. See P2-3 for what the matrix must
contain.

**Off-Git bytes.** Goal5848 archives now contain their exact native, Direct,
PyOptix, PTX, CUBIN and receipts, which is a real improvement over Goal5838 and
Goal5840. But the archives themselves, and the older Goal5838/5840 provider
binaries, remain outside Git. The artifact must state which authorities cannot
be replayed from the repository alone and what a rebuild requires.

## 13. Manuscript claim ledger

**Supported as written.**

- The complete cross-role callback protocol is the compilation and admission
  unit; five obligations are discharged as one set before lowering.
- Admission, canonical planning, identity, provider binding and lifecycle are
  schema-parametric; executable lowering is compiler-owned and
  topology-specific.
- Restricted-Python callback source is parsed as data and never imported or
  executed as host Python.
- Sphere and curve routes use OptiX built-in intersection modules with no user
  intersection program, enforced fail-closed in the native provider.
- A separately implemented checker, importing none of the implementation and
  refusing compiler-produced projections, verified five declared properties
  across three route groups and four modes, rejecting 15 unique mutations.
- Bounded application-neutral owner-grouped Boolean any-hit behaviour exists in
  the engine while collision construction, interpretation and oracle remain in
  the case study.
- Status precedes output publication on every path; native and compact status
  are synchronous gates and the output oracle is checked before return.
- Every adverse transaction in the Goal5842–Goal5851 chain is retained and
  unpooled.

**Supported only after rewrite.**

- *Prospective extension.* Must read "one prospective compositional-extension
  result over a frozen author-defined ten-row domain", past tense, bound to
  `7da6805`, with the post-selection topology-specific cost stated.
- *Leaf-kind coverage.* Must read "one bounded public route per pinned OptiX
  leaf-primitive kind"; 4/4 is kind presence, and build-input coverage remains
  2/6.
- *Steady performance.* Must name the two frozen tasks, both GPU generations,
  the prepared-replay contract, the competence-gated baseline, and the
  median-only nature of the Direct gate. "Within 1.20x of Direct on the median
  for these two tasks", never "parity", never "speedup".
- *First result.* Only as the dual-endpoint bracket with the causal sentence in
  Section 10.
- *Independent checking.* Must carry the three-route, four-mode, five-property
  denominator in the same sentence.
- *Failure semantics.* Must carry the double-fault limitation.
- *Receipts.* Must not claim every measurement receipt field is eagerly
  validated before scalar output is observable.

**Forbidden.**

- Topology-generic or arbitrary Callback IR lowering or execution.
- "Unbiased", "blind", or "representative" for the Goal5838 selection.
- Any intrinsic language or compiler speedup, from either first-result endpoint.
- The Goal5845 9.53x reciprocal, and Goal5847's 0.229x complete-process ratio.
- "Confirmatory" for the final transactions.
- Direct parity, a Direct tail bound, or borrowing 1.35x as a Direct gate.
- Any ease-of-use, productivity, learnability or usability claim.
- Any real-world protocol-defect prevalence claim.
- Universal negligible overhead, cold-start parity, or hardware-independent
  speedup.
- Any public claim at all while the authority holds
  `public_or_manuscript_claim_authorized: false` and
  `external_review_complete: false`.

## 14. Smallest credible repair plan

Five actions, ordered by submission value.

1. **Rewrite the manuscript's architecture, evaluation and claims sections.**
   Adopt the schema-parametric / topology-specific framing; replace the
   coverage counts; replace the entire evaluation with the two-generation
   `d653fe4` results; add RTX 4090 and RTX 3090 rows; add the limitations
   paragraph. ~14 focused hours. **Start now; this is the deadline.**
2. **Demote implementation-entry and adopt the dual-endpoint presentation.**
   Headline becomes prepared steady public RTDL/Direct. First result appears
   only as the bracket with the Section 10 causal sentence. ~2 hours, and
   non-negotiable — leading with 0.62x would be fatal at review.
3. **Disclose the provider double-fault; do not repair.** One limitation
   paragraph plus one sentence in the artifact notes. ~1 hour.
   In the same pass, report the post-import **range** rather than only its
   median (worst block 2.377129x, Ampere relation), and state that the
   successor/predecessor control is registered on steady execution only and is
   adverse on both first-result endpoints (P1-3). ~1 hour.
4. **Complete `KNOWN_STALE_CUSTODY_CHECKS.md` with Goal5837 and Goal5843, and
   ship a layered artifact test matrix** naming expected-green suites,
   expected-red historical checks with reasons, and hardware-gated suites.
   ~2 hours.
5. **Fix the malformed Ada digest in the review packet and state the
   portable-versus-full authority distinction in the artifact README.**
   ~1 hour.

Explicitly **not** required before submission, with the claim each omission
costs: external human authoring (costs all usability language, already
forbidden); real-world prevalence (costs the empirical motivation, replace with
constructed defect classes); a third task or application (costs nothing — a
count is not generality); repairing the near-parallel Boolean guard (costs a
narrowed case-study claim, already narrowed); and any further performance
engineering (costs nothing; the evidence is sufficient and further tuning would
only deepen the task-tuning concern in P1-2).

## 15. Final verdict

**`SUBMIT_AFTER_BOUNDED_REWRITE`**, conditioned on action 2 being treated as
binding rather than advisory.

**Rationale.** Every blocker I found is a claim or presentation blocker, not an
evidence blocker. The architecture is now described accurately by the authors
themselves — the single largest correction from my previous review, made
without argument. The independent checker is genuine and correctly scoped. The
performance evidence, subject to the recount this session could not perform, is
the strongest artifact the project has produced: same source, two GPU
generations, a device-continuation baseline proven competent, zero retry and
zero discard, a passing regression control, and a public fully checked path at
1.077x–1.175x of purpose-built Direct CUDA/OptiX. The adverse-custody discipline
across Goals 5842–5851 is better than I typically see and should itself be
described in the paper.

Two things stand between this and a defensible submission. The manuscript
contains none of it and has not been started, with under two days to freeze.
And the metric that decides PASS was moved, after an adverse observation, onto
an endpoint whose favorable direction comes from the baseline's dependency
import — the same confound the project correctly refused in Goal5847. The first
is work. The second is a presentation rule that costs two hours and, if
ignored, would convert a good bounded result into an overclaim a CGO reviewer
would catch.

I do not recommend `PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`, because none
of the listed items requires new measurement, new engineering, or a source
change; all five are writing and disclosure. I do not recommend `DO_NOT_SUBMIT`,
because the bounded contribution is real, the evidence supports it, and the
non-claims are already correctly enumerated by the authors.

One procedural note, per Section 12 of the call: this verdict authorizes
nothing on its own. The authority still holds
`public_or_manuscript_claim_authorized: false` and
`external_review_complete: false`, and this review does not change either. What
it does establish is that the evidence recounts: every registered figure in the
Goal5851 report reproduces from the raw samples, and I found no fabricated,
pooled, discarded or misattributed row.
