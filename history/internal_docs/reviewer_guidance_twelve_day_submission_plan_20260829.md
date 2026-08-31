# Reviewer guidance — the twelve days before a fixed 2026-09-10 submission

**From:** the external adversarial reviewer
**Date:** 2026-08-29
**Constraint accepted:** submission on 2026-09-10 is fixed and non-negotiable.
**Status:** advisory. Authorizes nothing.

---

## 0. The objective changes, and this changes the plan

Strong accept is off the table for this cycle. That means the submission now has **two** purposes, and the second one is worth more than most people realise:

1. **Maximise the probability of accept** on the evidence that exists.
2. **Maximise the quality of the reviews you get back**, because those reviews are the highest-value input available to the follow-on programme — three or four adversarial experts from exactly your target community, for free.

Optimising for (2) is a different writing task from optimising for (1), and it is mostly free. A paper that names its gaps specifically and ranks them gets reviews that tell you *which gap the community actually cares about*. A paper that hedges vaguely gets reviews that tell you nothing you did not know.

**Everything below is ordered by risk-reduction per day, not by evidence value.** The high-evidence-value items (real-bug corpus, generic schema compiler, external authors, formal theorem) are all follow-on work and must not be attempted now.

---

## 1. The paper's four fatal risks, in order

| # | Risk | Why fatal | Cost to remove |
|---|---|---|---|
| **R1** | The paper does not cite `OptixPayloadType` / `OptixPayloadSemantics`, DXR Payload Access Qualifiers, or Vulkan cross-stage interface matching | A CGO RT reviewer knows these. A paper claiming novelty for payload/attribute ABI checking that does not mention the platform's own per-word, per-stage access contract reads as ignorance or concealment. Both are desk-level damage. | **half a day of writing** |
| **R2** | CP002's residual was measured against baselines that did not declare payload types | Same class of error as Goal5798's asymmetric baseline, in the novelty dimension. If a reviewer suspects it, the whole residual table is suspect. | **1.5–2 days if re-run; half a day if disclosed** |
| **R3** | The Direct arm prepares 120–190 ms *slower* than PyOptiX, unexplained | Expert C++ as the slowest arm reads as a straw-man baseline and contaminates the steady rows that carry your actual result | **1 day (description, no rerun)** |
| **R4** | Double-blind violation in manuscript or artifact | Desk reject; wastes everything else | **2 days, Sep 7–9** |

R1 is the one I missed for eight cycles and it is now the highest-priority item in the paper.

---

## 2. What the native-mechanism boundary actually is

I verified this. `OptixPayloadSemantics` provides, per payload word, per program type — `TRACE_CALLER`, `CH`, `MS`, `AH`, `IS` — one of `NONE` / `READ` / `WRITE` / `READ_WRITE`, bound through `OptixPayloadType { numPayloadValues; payloadSemantics }`, with mismatches diagnosable under OptiX-IR. DXR has Payload Access Qualifiers. Vulkan requires payload and hit-attribute structures to match across stages.

**What that covers:** per-slot *access and ownership* on the **payload** path — who may read, who may write, in which stage.

**What it does not cover, and this is your residual:**

1. **Nominal application meaning.** Two `u32` words, both `CH_WRITE | TRACE_CALLER_READ`: one is a count, one is an index. No platform mechanism distinguishes them.
2. **Attributes.** OptiX exposes `numAttributeValues` but **no per-attribute access semantics**. Your executed CP002 counterexample — `optixReportIntersection(0.0f, 0u, item.item_id)` changed to `primitive_index` — is an *attribute* defect, not a payload defect. **Verify this and say it precisely; if it holds, CP002 survives the strongest native configuration intact.**
3. **Cross-role production ordering** (CP001) — access qualifiers say who *may* read or write, not that a producer actually produced before a consumer read.
4. **Physical geometry/SBT binding consistency** (CP003), **status-before-host-consume** (CP004), **checked-program-to-executable identity** (CP005) — untouched by any of the three platforms.

**Predicted outcome of the kill-test: the residual survives but narrows on the payload path.** That is a better paper, not a worse one — a residual that survives the platform's strongest configuration is worth far more than one measured against defaults.

---

## 3. The twelve days

### Aug 30 (Sun) — decide the spine

**Morning.** Run the reduced kill-test setup: enable `OptixPayloadType` with full per-stage semantics on the PyOptiX arm; re-run the five counterexamples; record per counterexample whether OptiX validation now catches it. This is a configuration change and a re-run of an existing harness, not new engineering.

**Afternoon.** Write **both** versions of the one-sentence contribution — one assuming the payload half is conceded to the platform, one assuming it is not — so that whichever way the test goes, the writing week begins with a fixed spine. Do not start the manuscript before this sentence is frozen.

**If the test cannot be run cleanly by end of day, stop trying and go to disclosure** (Aug 31 item 2). Do not spend Aug 31 on it.

### Aug 31 (Mon) — close R1, R2, R3

1. **Related-work paragraph on native mechanisms.** Cite the three platform mechanisms; state the four-item boundary from §2 above. Whether or not the kill-test ran. **This is the highest-value paragraph in the paper.**
2. **Baseline configuration disclosure.** State exactly what payload-type configuration each arm used in the Goal5800 residual experiment. If defaults were used, say so and state which half of CP002 that affects. Honest disclosure of a weakened configuration costs you a sentence; a reviewer discovering it costs you the paper.
3. **Direct prepare-phase composition.** What each arm does between process start and prepared state — specifically whether module/PTX construction happens inside `PREPARE` for Direct but not for the Python arms. If the phases are not composition-matched, say so in the table caption. No rerun required; this is a description of frozen code.
4. **Absolute times.** Per arm × task × regime medians in milliseconds. Restate the headline as *one-time ~163–223 ms admission cost, no measurable per-execution cost* instead of *1.48–1.79× cold and prepare*. Same data; the ratio framing is actively hurting you.

### Sep 1–6 — writing week, protected

No engineering. Structure:

- **Abstract carries the limits**: two closed public protocol families; zero prospective exams; zero third-party authors. If those three facts cannot survive in the abstract, the contribution sentence is still too broad.
- **The oracle paragraph** (2 hours, high value). Every one of the five defects reaches launch with OptiX validation PASS, CUDA SUCCESS, exit 0, no exception, through both PyOptiX and OWL. Then the three-part reply: (i) every automatic check in the platform reports success — measured, not asserted; (ii) an oracle covers only the inputs it covers, and CP004 is capacity-dependent and invisible below capacity; (iii) the premise of repurposing RT hardware is that you do not already have a fast correct answer, so requiring an independent correct implementation as your only defence is an unsatisfying position.
- **All negatives in the body**: 2/6 gates, the Direct rows, 6/15 compatible with 9/15 UNKNOWN, and the three zeros — adjacent to the favourable result each qualifies, never in a footnote.
- **A specific, ranked limitations section** — see §5.
- **Use the pages.** You are at 7 of 11. Fill them with the per-mechanism OWL residual table, the 19-leaf table, absolute times, the native-mechanism boundary, and the phase composition. **Do not fill them with process or governance narrative** — reviewers punish volume that is not evidence.

### Sep 7–9 — anonymisation and closure

- Two **separately gated** double-blind passes: artifact/evidence, then manuscript. Named owner for each, frozen scrub checklist. Scrub system history, host identity, IP addresses, personal filesystem paths, internal goal numbering, and reviewer-facing custody data.
- **Withdrawn-result scan**: an explicit search of manuscript, figures and artifact for the Goal5798 v11 prepared win and for the Goal5807 boundary passes (`HARNESS_RUN_ENTRY_TO_FIRST_EXACT_OUTPUT`, `APP_PREPARE_PLUS_FIRST_EXACT_EXECUTE`). Both are permanently withdrawn and both will look available under deadline pressure.
- Artifact `verify.py` run from a clean checkout; bootstrap specification (per-row seed derivation, `randrange` resampling, index `int(p·(n−1))`) written into the methods or README.

### Sep 10 — upload.

---

## 4. Optional, in strict priority order, only if a second person is genuinely free

**O1 — "nowhere enforced" scan (2–3 days, no GPU).** For 3–4 published open-source RT-repurposing artifacts, answer one question per artifact: *is any of the five protocol properties enforced anywhere in this code?* The answer is almost certainly no in all of them, and "in N examined artifacts, none enforces any of these five properties" is a real, cheap, low-risk empirical statement that converts the problem from asserted to observed.

**Deliberately not a bug hunt.** No defect classification, no annotator protocol, no responsible-disclosure process, no capture rate. Those belong to the follow-on programme and deserve to be done properly in October, not badly in September. Attempting the full corpus now risks producing a weak version of your best future asset.

**O2 — checker-off setup ablation (1–2 days).** Of the +163–223 ms, how much is admission? Only if it does not touch the writing week. If skipped, write one sentence: *we cannot yet separate admission cost from total lifecycle cost; isolating it requires a bypass arm with byte-identical execution artifacts and is future work.* Pre-empting the question honestly is worth most of what the experiment would buy.

---

## 5. Write the limitations section to buy good reviews

This is the cheapest high-value thing in the whole plan and almost nobody does it.

Do not write a hedge list. Write a **specific, ranked, falsifiable** statement of what is missing, and ask:

> The three gaps we consider most consequential are, in order: (a) generic authoring — arbitrary verified Callback IR is not yet GPU-executable, so the admission model is demonstrated over two closed protocol families; (b) defect prevalence — our five counterexamples are constructed, and we have not established that these defects occur in released third-party code; (c) external authorship — all applications were written by the authors, and no third party has used the public interface. We would value reviewer guidance on which of these most affects the contribution's value.

Reviewers answer questions like that. The answer tells you where to spend the next three months, and it comes from people who decide what gets accepted at this venue. That single paragraph may be worth more than any experiment you could run in twelve days.

---

## 6. Forbidden, for the next twelve days

Each of these is something your own record shows you can do in good faith under pressure.

1. **No new measurement boundary, regime, prefix or derived quantity.** Goal5807 happened once.
2. **No arm-specific optimisation.** Goal5798 happened once, and cost you your only favourable result. If you optimise RTDL, you must audit the other arms equally — so optimise nothing.
3. **No third task, no re-tuned timing, no new performance matrix.**
4. **No core changes.** The generic schema compiler is follow-on work; touching the core now invalidates every frozen artifact and every hash in the record.
5. **No prospective exam attempt.** If it cannot be run properly, the count stays zero and the paper says zero.
6. **No agent proxy as usability evidence.** Categorical reporting only, or omit it. `third_party_human_author_count` stays 0.
7. **No padding.** 7 of 11 pages filled with evidence beats 11 of 11 with narrative.
8. **No resurrection of withdrawn results.** Scan for them explicitly.

---

## 7. What to expect, stated plainly

With the plan above executed, my honest estimate of the outcome is **borderline, with a real chance of accept and a real chance of reject**, most likely turning on whether the reviewers weigh the mechanism idea or the two-family limit more heavily.

The likely review comments, so you can pre-empt them in the paper rather than in the rebuttal:

- *"Two author-designed tasks, two hardcoded protocol families — is this a compiler or two library entry points?"* → the honest answer is in your capability table; make sure it is in the abstract too.
- *"OptiX/DXR already have payload access qualifiers."* → R1 and §2.
- *"Wouldn't the developer's own test catch these?"* → the oracle paragraph.
- *"Your Direct baseline prepares slower than Python."* → R3.
- *"No external users, no prospective evaluation."* → true; say so first, and rank it.

A rejection here is not a failure. It buys you the reviews, and the follow-on programme is materially better with them than without them. The one outcome that would be a failure is an accept obtained by overstating — and after eight cycles I do not believe that is a risk you are running.

---

*Advisory only. Authorizes no experiment, no execution, no claim and no submission. Prospective new-application exams: 0. Third-party human authors: 0. Usability studies: 0. Public closed GPU protocol families: 2.*
