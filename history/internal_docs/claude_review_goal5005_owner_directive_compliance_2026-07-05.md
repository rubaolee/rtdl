# Claude Review — Goal5005 Owner-Directive Compliance (Fresh Headline + Device-Resident Gate)

Date: 2026-07-05
Reviewer: Claude (strict)
Under review: `goal5005_owner_directive_fresh_headline_and_device_resident_gate_2026-07-05.md`
+ artifacts + measurement script.

## Verdict

```text
approve_goal5005_stop_device_resident_track__require_cold_process_disclosure_before_closeout
```

Approve the directive compliance — it is complete and honest, and it was done against the
team's own prior narrative, which is exactly the behavior this loop is for. Fast-pack
~4.22 s is now the headline, device-resident is stopped
(`device_resident_payoff_not_demonstrated_stop_track_for_v2_14_3`), the accounting delta is
correctly isolated, false precision is gone, and replay/query-many are disallowed.

**But this goal surfaced a number that cuts one level deeper than the directive asked, and
the closeout docs must confront it before headlining 4.22 s:** the new OS-process-cold
measurements show a real one-shot CLI invocation is **~11.6 s median (5.9–33 s)**, not
4.22 s. The 4.22 s figure is *long-lived-process* fresh — it excludes ~7 s of process /
runtime / first-call cold-start. So the same favorable-regime pattern we just corrected
(replay→fresh) exists one level up (warm-process-fresh→cold-process-one-shot), and it must
be disclosed, not inherited silently.

## What was done correctly (credit)

- **Action 1 enforced.** Fast-pack ~4.22 s is the headline; device-resident ~5.0 s is
  labeled experimental / slower-in-fresh / payoff-not-demonstrated. ✓
- **Action 2 done right — and this is the good part.** The accounting delta is isolated
  **same-artifact, old-key vs corrected-key = median 0.129 s** (replay 0.003 s). The report
  explicitly states the `4.816 → 5.004` cross-run movement must **not** be attributed to the
  accounting fix — the true correction is ~0.13 s, the rest is variance. This is precisely
  the isolation I required, and it is correct. False precision (`5.003915 s`) is dropped for
  rounded, regime-labeled values. ✓
- **Action 3 done.** Replay and prewarm recomputed on corrected accounting; replay
  disallowed as fresh/query-many. ✓
- **Action 4 gate → STOP.** Neither payoff (distinct-input query-many, nor a real downstream
  device operator beating fast-pack) was demonstrated, so the track is stopped for v2.14.3,
  code kept behind flags. Correct and disciplined. ✓
- Generic boundary preserved; structural anchors stable (428322 / 15014). ✓

## The new finding: 4.22 s is warm-process; the real one-shot is ~11.6 s (AM1, required)

The report's own regime table now distinguishes **OS-process-cold** (new Python process per
run) from **long-lived-process fresh** (runtime already alive). The cold numbers:

```text
Fast-pack cold:          median 11.714 s   (min 5.912 s, max 33.226 s)
Device-resident cold:    median 11.565 s   (min 8.117 s, max 24.059 s)
Long-lived-process fresh: ~4.22 s (fast-pack) / ~5.0 s (device-resident)
```

A user who runs `python section57_overlay_columnar_binary.py ...` **once** gets the
cold-process path — process start + Numba/OptiX/CUDA context init + first-call JIT — i.e.
**~11.6 s median, and never below ~5.9 s**, not 4.22 s. The 4.22 s headline assumes the
runtime is *already warm in a live process*, which only happens if something already ran in
that process. So "4.22 s fresh one-shot" has, this whole time, been excluding runtime
cold-start.

Required before closeout:
- **Do not present 4.22 s as the raw single-invocation cost.** State the deployment regime it
  assumes: "per-overlay cost in a warm long-lived process (runtime already initialized)."
- **Disclose the cold-process one-shot regime** as the cost a CLI user actually pays for a
  single run, and state which regime v2.14.3 intends as its product model (CLI one-shot vs
  warm service/library). If undecided, present the regime ladder and pick no single headline.
- The honest ladder:
  ```text
  CLI one-shot (cold process)      ~ (needs a clean re-measure; this session ~11.6 s median, high variance)
  warm-process fresh overlay       ~4.22 s (fast-pack)   ← current headline; label the assumption
  same-input prepared replay       ~0.32–0.92 s (diagnostic only)
  true query-many                  not demonstrated
  ```

## This measurement session is environment-noisy — don't lock any absolute from it (AM2)

The session shows signs of heavy POD contention: replay worst `23.182 s`, prewarm route
elapsed `50.095 s` / hot `24.741 s`, cold spread `5.9–33.2 s` (5.6x). These are not stable
enough to cite as absolutes. The report correctly does **not** headline this session's
numbers (the 4.22 s headline comes from the cleaner Goal4985/4977 session) and uses this
session only for the qualitative conclusions that are robust to noise: "device-resident does
not win fresh" and "cold is high-variance." That is a legitimate use of noisy data. But:
- **Re-measure the cold-process regime on a quiet POD** (median-of-≥10, control contention,
  separate runtime-init from compute) before citing any cold number in the closeout docs.
- Keep the 4.22 s headline sourced to the clean session, labeled with its warm-process
  regime; do not silently blend it with this session's noisy 11.6 s.

## Framing recommendation (AM3)

Stop searching for a single flattering headline number. v2.14.3 has a **regime ladder**, and
the honest doc presents the ladder with each number's regime and exclusions. If a single
headline is contractually required, it must be labeled ("~4.22 s per overlay, warm
long-lived process, excludes runtime cold-start; cold CLI one-shot is materially higher").
This is the same discipline that fixed replay→fresh; apply it to warm→cold.

## Answers to the review questions

1. Headline uses fast-pack fresh, not slower device-resident? **Yes.**
2. Device-resident classified as experimental, fresh payoff not demonstrated? **Yes.**
3. Accounting handled correctly (fresh delta ~0.129 s, replay ~0.003 s, cross-run not
   misattributed)? **Yes — correctly isolated.**
4. Separates OS-cold / long-lived fresh / replay / query-many? **Yes — and that separation is
   what exposes AM1: the headline sits in the warm-process rung, not the cold one-shot rung.**
5. Cold-process runs interpreted as high-variance diagnostics, not a headline? **Yes — but
   the docs must still disclose cold as the real CLI one-shot cost (AM1), re-measured clean
   (AM2).**
6. Replay still disallowed as fresh/query-many? **Yes.**
7. `device_resident_payoff_not_demonstrated_stop_track` justified? **Yes.**
8. Generic boundary preserved, no RayJoin-specific core win? **Yes.**
9. Proceed to closeout only after adopting corrected framing? **Yes — plus AM1–AM3.**

## Non-authorization

Approves the stop-device-resident decision and the fast-pack headline. Before closeout docs:
no presenting 4.22 s as the raw single-invocation cost without its warm-process label; no
citing this noisy session's absolutes; no cold-process number in docs until re-measured on a
quiet POD; and the standing bans hold (no author parity/ratio, no replay/query-many headline,
no broad speedup, no RayJoin-specific core semantics). The honest one-line status: v2.14.3's
writer-free binary route costs ~4.22 s per overlay in a warm long-lived process (fast-pack;
device-resident is slower and stopped), while a cold CLI one-shot is materially higher and
needs a clean re-measure.
