# Owner Directive — Preconditions Before "Go Do" The 10x Plan

Date: 2026-07-05
From: owner (via Claude review)
To: main implementation AI
Status: required before any 10x implementation goal

This gates the "去做" authorization for the 4.22 s → 0.42 s (10x) plan. The plan is not
rejected, but it must not start as written, because as stated it would reproduce the
replay-masquerading-as-fresh pattern that has already been corrected three times.

## Ground truth this directive is built on

- `~4.22 s` is **warm long-lived-process, per-overlay** fresh — NOT the cold CLI one-shot
  cost. A cold one-shot is materially higher (~11.6 s median this session, high variance).
  Every performance statement must carry its regime label.
- The `~2.7 s` LSI producer splits into:
  - `~0.95 s` compile (`exact_pipeline_ensure + split_kernel_ensure`) — **AOT/prewarmable**
    (Goal5002 proved it drops to ~1e-6 s).
  - `~1.7 s` per-input workspace (`grouped_range_ensure + scaled_cache_ensure`) — Goal5003
    proved this is **scale-domain-dependent and intrinsic per distinct domain**; it does NOT
    prepare away for a distinct-domain fresh overlay. It DOES reuse to ~0.14 s for a new
    query in the **same base / same scale domain**.
- Therefore:
  - Distinct-domain fresh floor ≈ `~1.7 s LSI workspace + ~0.25 s best-case device downstream ≈ ~2 s` (≈2x, NOT 10x).
  - 10x to ~0.42 s is achievable ONLY in a **prepared-base + many distinct same-domain queries** regime (supported by Goal5003's 0.14 s reuse), which is **not yet demonstrated**.

## Precondition 1 — Declare the target regime in the plan's first line

The 10x plan must state, up front, that ~0.42 s is a **prepared-base / same-domain
query-many** target, not a fresh distinct-domain one-shot target. It must also state the
honest distinct-domain fresh floor (~2 s, ~2x). No "LSI 2.7 s → 0.1–0.2 s" bullet without
the Goal5003 caveat that ~1.7 s of it is per-input-intrinsic for a distinct domain.

Acceptance: the plan names the regime for the 10x target in its opening, and states the
~2 s distinct-domain fresh floor alongside it. Fail if 0.42 s appears without its regime.

## Precondition 2 — Demonstrate the query-many regime with DISTINCT inputs before optimizing it

Before any implementation goal that targets the prepared/query-many 10x:
- Measure one prepared base LSI serving **≥3 distinct query inputs in the same scale
  domain**, each timed separately (expect ~0.14–0.3 s LSI/query per Goal5003, plus
  downstream), and one **distinct-domain** query (expect the full ~1.7 s workspace rebuild).
- This proves the regime exists and quantifies its real per-query cost — not a repeat of the
  same input (which is replay, already disallowed).

Acceptance: a measured table of ≥3 distinct same-domain queries + 1 distinct-domain query,
fresh-labeled. No `query-many` wording anywhere until this table exists. If it cannot be
produced (e.g., no distinct inputs on the POD), the 10x prepared target is **not authorized**
and work stops at Precondition 3's safe items only.

## Precondition 3 — Do the two regime-independent wins first, measured in fresh

These help BOTH warm-process fresh and query-many, are generic, and carry low risk. Do them
first and measure their effect on the **warm-process fresh** number (not replay):
1. **AOT / prewarm the ~0.95 s compile** (exact pipeline + split kernel) as a reusable
   precompiled pipeline. Report fresh before/after. Prewarm time reported separately, never
   folded into the route window.
2. **Replace the bitonic sort with a generic GPU ordering primitive** (CUB / Thrust /
   CuPy-backed segmented sort). Must be generic (no RayJoin-specific sorter), structurally
   equivalent (same 428322/15014 anchors), fresh-measured.

Acceptance: fresh warm-process number reported before/after each, with variance (median-of-N),
same clean POD. Expected combined effect ≈ compile ~0.95 s removed + sort share of downstream
reduced — i.e. a real but sub-2x fresh improvement, honestly labeled (not 10x).

## Precondition 4 — The device-resident downstream redo must re-pass the payoff gate

Device-resident was STOPPED one goal ago (`device_resident_payoff_not_demonstrated`). A redo
is allowed, but it re-enters through the SAME gate, not around it:
- No device-resident implementation goal until Precondition 2's query-many table exists AND a
  minimal device-resident downstream is shown to **beat** the fast-pack path **in that
  regime, end-to-end, with numbers**.
- If it cannot beat fast-pack in the target regime, it stays experimental behind its flag;
  no further goals.

Acceptance: device-resident redo cites a measured win in the declared target regime before
any optimization goals are spent. Fresh regression (as in Goal4998/4999) = stop again.

## Order

```text
P1 (declare regime + fresh floor)
 -> P3 (AOT compile + generic sort, measured in fresh)     [safe, do now]
 -> P2 (demonstrate distinct-input query-many)             [gate for the 10x target]
 -> P4 (device-resident redo only if P2 holds and it wins) [gated]
```

Do P3 now regardless — it is a real fresh win with no regime risk. Do P2 before claiming any
10x. Do P4 only through the gate.

## Non-authorization

No 0.42 s / 10x claim without the prepared same-domain query-many regime named and measured;
no `query-many` wording without a distinct-input table; no presenting warm-process fresh as
the cold one-shot cost; no device-resident performance goals before a measured regime win; no
RayJoin-specific core sorter/workspace; no author `0.04 s` anchoring — the target is 10x from
4.22 s, i.e. ~0.42 s, and only in the regime where that is physically reachable.

## One line

10x to ~0.42 s is a prepared-base same-domain query-many target, not a fresh one-shot target.
Prove that regime with distinct inputs first; do the AOT-compile and generic-sort fresh wins
now; and re-gate the device-resident redo that was just stopped. Distinct-domain fresh floors
around ~2 s — do not sell it as 10x.
