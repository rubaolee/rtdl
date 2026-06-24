# Proposed V3 Redesign: Build the Runtime Trunk First

Date: 2026-06-22
Author: Claude (independent reviewer) — **proposed redesign / recommendation, not a release authorization**
Companion to: `claude_phoenix_v3_external_review_2026-06-22.md`, `phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`
Status: for the release owner to accept, amend, or reject. It does not change the mandate or the release gate by itself.

---

## 0. The one-sentence diagnosis this redesign is built on

V3 was defined by a **performance promise without a performance source**. Same backends (OptiX/Embree), same hardware as V2.14, same primitives — so broad speedup can only come from one place: a **cross-phase, residency-aware execution runtime**. That runtime was designed but never turned on (`m2_no_execution_skeleton`, `runtime_executed: False`), and the real lever (device residency between phases) was frozen by V4-scope fear. So all effort went into per-route cache hygiene, which only repays V3's own overhead and asymptotes to parity. The redesign fixes the *order* and the *measurement*, not the people.

## 1. What V3 actually is (identity correction — read first)

V3 is **the productized, residency-aware execution runtime for RTDL.** It is a *capability* release, not a uniform-speedup release.

- A capability proves itself by winning on the workloads it targets (multi-phase, residency-rich) and staying at parity where it cannot help (single-shot, backend-ceiling). It does **not** prove itself by a uniform speedup tax across every app.
- The benchmark apps are **probes**, never the optimization target. "13 rows look okay" is not "the runtime improved."
- Success is measured on two populations (Set A / Set B), and a win only counts if it comes from the runtime, not from a per-route cache. See the Set-A/Set-B bar proposal.

## 2. The one rule that governs every task

> **Every optimization must land as a reusable runtime capability that flows through the single execution path. If a change cannot be expressed that way, it is not V3 core work.**

This rule exists to kill the failure mode that produced 1.012x: independent leaf fixes that never sum to a broad effect. One load-bearing mechanism (the execution runtime), improved once, must lift many probes at once. If a fix only helps one row and bypasses the runtime, it is hygiene at best and a distraction at worst.

## 3. The V3 / V4 boundary line (so residency is usable)

State this once and enforce it, so residency work stops being blocked by V4 anxiety:

- **Internal residency between RTDL's own phases = V3.** Keeping intermediates device-resident from one RTDL phase to the next, with the host boundary only at the final result.
- **Exposing device buffers to an external host (CuPy/Numba/PyTorch/C) = V4.** Different owner of the buffer; out of scope here.

The test is *who owns the buffer*. If RTDL owns it across its own phases, it is V3.

---

## 4. THE ORDER (at a glance)

```text
Step 0  Stop & freeze    end the cache thread; freeze Set-A/Set-B; adopt 2-number scorecard; no all-app runs
Step 1  Build the trunk  make the execution graph EXECUTE on ONE residency-rich family, end to end
Step 2  Generalize       route a 2nd and 3rd Set-A family through the SAME runner (prove it is general)
Step 3  Residency default phase accounting + device residency between phases as the runner default
Step 4  Continuation core promote grouped-reduction / component-union / ranked-summary into runner nodes
Step 5  First all-app run only now; read on Set-A/Set-B; against the redefined bar
Step 6  External review   per protocol; release decision
```

Dependencies are strict: **do not start Step N+1 until Step N's exit criteria pass.** The whole point of the redesign is that the trunk (Steps 1–2) comes before the leaves, the reverse of what produced 1.012x.

---

## 5. The order, in detail

### Step 0 — Stop and freeze (do this before any new engineering)

- **Stop the symbol/query-cache thread.** It is proven hygiene (1.001x). Anything already landed and at parity, keep; do not chase more.
- **Freeze the benchmark set into Set A / Set B** with a one-line rationale per row, committed before any run. No reclassification after results.
- **Adopt the two-number scorecard** as the only release read.
- **Freeze all-app paired runs** until the trunk executes (Step 1–2). They will only re-confirm 1.01x and burn pod time.

Exit: cache thread closed; A/B list committed; scorecard adopted; all-app paused.

### Step 1 — Build the trunk: make the execution graph EXECUTE

This is the heart. Turn the design-language layer into a running prepared-session runner.

- Flip `V3_EXECUTION_GRAPH_STATUS` off `m2_no_execution_skeleton` and `v3_0_prepared_graph_chunk_executor.py` off `runtime_executed: False` **for one residency-rich family, end to end.**
- First family: **fixed-radius self-query → grouped-stream continuation** (the pieces already exist in `partner_adapters.py` / the self-query device-column primitive). Route it entirely through the runner, with intermediates kept device-resident between phases.
- Produce focused evidence on that **one** probe (a Set-A member, e.g. RT-DBSCAN) showing a material gain that comes from the runner.

Exit criteria:
- `runtime_executed: True` for that family.
- One Set-A probe runs *entirely* through the runner (no bypass).
- Focused evidence: material per-probe gain, device residency across phases (internal, V3-scoped).

What this step is **not**: an abstract runner with nothing flowing through it (that is how you got `runtime_executed: False`); and not a special-cased fast path for one app (the runner must be written to generalize).

### Step 2 — Generalize the trunk (prove it is not a one-off)

- Route a **second and third Set-A family** through the *same* runner. Choose families that exercise different shapes: a component-union one (RT-DBSCAN if not used in Step 1), and a genuinely multi-phase one (RayJoin LSI→PIP→overlay, or Barnes-Hut frontier accumulation).
- The goal is to prove the runner is **general**: the same execution path serves multiple families without per-family bypass.

Exit criteria:
- ≥3 Set-A families flow through the single runner.
- Per-probe focused evidence for each.
- No family quietly bypasses the runner to "look fast."

### Step 3 — Make residency the default discipline

- Add **phase accounting as a first-class runtime output**: per-phase timing and a measured "no host materialization in the hot path" flag, not a metadata assertion.
- Make **device-resident intermediates between phases the runner's default**, within the V3 line (§3).

Exit criteria:
- Set-A probes show measured device residency across phases.
- "No host stage in the hot path" is *measured*, not claimed.

### Step 4 — Promote the continuation layer into the generic core

- Turn the continuation families (grouped reduction, component union, ranked summary, frontier/vector accumulation) into **runner-callable nodes**, not app-mode code.
- Pick the family with the most cross-app reuse first (grouped reduction spans RT-DBSCAN, RTNN, RayDB).

Exit criteria:
- Continuation is a layer the runner calls, not route-shaped code in app modes.

### Step 5 — First serious all-app paired run

- **Only now.** Precondition: the runner executes on ≥3 Set-A probes with material per-probe gains, and residency is the default.
- Run the same-hardware all-app paired suite; read it on the Set-A / Set-B scorecard, against the redefined bar.

Exit criteria:
- Set A clears its material bar **from the runtime path**; Set B at parity-with-explanation; every surprising row explained in user language.

### Step 6 — External review and release decision

- Per `phoenix_v3_bounded_external_review_protocol_2026-06-22.md`. No release wording before a real external verdict against the redefined bar.

---

## 6. What to reject (anti-patterns that recreate 1.012x)

- **Row-by-row regression chasing.** Each cache may be generic, but the *pattern* asymptotes to parity. Reject it as a strategy.
- **App-specific native ABI / app semantics in the engine.** Keep the engine app-agnostic.
- **An abstract runner with nothing flowing through it.** Step 1 must execute a real family.
- **A hardened family that bypasses the runner.** That is how continuation stayed route-shaped.
- **Counting green unit tests as progress.** Only the same-hardware paired number on the scorecard counts.
- **Reclassifying Set A/B after seeing results.** Freeze before the run.
- **All-app runs before the trunk executes.** They waste pod time and re-confirm parity.

## 7. Success definition (the bar)

Use the Set-A / Set-B two-number scorecard (`phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md`): Set A material superiority **sourced from the runtime**, Set B parity-with-explanation, classification frozen, wins not from caches. Single blended geomean is retired as the release read.

## 8. How this could still fail (honest risk register)

| Risk | Meaning | What to do |
| --- | --- | --- |
| Trunk delivers little even on Set A | V3's performance premise is wrong; the runtime does not compound | Then V3 is a *capability/quality* release, not a speed release — change the claim, do not fake the number |
| Residency keeps getting blocked as "V4" | The §3 line is not respected | Enforce the line: internal-between-phases = V3 |
| Runner adds overhead to Set B | New execution path taxes single-shot rows | Set-B parity gate (≥0.98x) catches it; fix or fast-path the bypass for trivial cases |
| Effort drifts back to leaves | Old habit returns | Rule §2: no change counts unless it flows through the runner |

## 9. The shortest possible statement of the redesign

Build the **trunk before the leaves**: make the execution runtime actually execute on one residency-rich family (Step 1), prove it generalizes (Step 2), make residency its default (Step 3), promote continuation into it (Step 4) — and only then measure all-app, on a scorecard that separates the workloads the runtime can win from the ones it can only match (Step 5). Define V3 as the runtime capability that earns its wins, not as a uniform speedup over V2 it has no physical source for.
