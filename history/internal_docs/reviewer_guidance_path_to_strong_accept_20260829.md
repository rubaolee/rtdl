# Reviewer guidance — what would make this a STRONG ACCEPT, and what it costs

**From:** the external adversarial reviewer, after eight review cycles
**Date:** 2026-08-29
**Status:** advisory. Authorizes nothing. Contains no new evidence.

---

## 0. The blunt answer first

**A strong accept is not reachable by 2026-09-10, and no amount of effort in the next twelve days changes that.**

This is not a documentation gap, a writing gap, or a presentation gap. Strong accept at CGO requires a reviewer to *champion* the paper against other reviewers, and champions are made by evidence categories this work does not yet have — not by better prose about the evidence it does have. Two of the three missing categories take months, not days, because they require building something (a general authoring path) or recruiting someone (an external user with an institutional determination).

**What you can reach by 2026-09-10 is a solid, defensible, honest accept-or-borderline paper.** What you can reach by roughly February–April 2027 is a genuine strong-accept candidate. This document is about how to get from one to the other, and about which of the two you should aim the September submission at.

I am telling you this because "不惜一切代价" is exactly the state of mind in which good projects destroy themselves in the last two weeks. §7 is about that specifically, and it is the most important section for the next twelve days.

---

## 1. What actually separates "accept" from "strong accept"

Sitting on a program committee, the mental move from *"this is fine, I'd accept it"* to *"I will argue for this paper"* almost always requires at least three of the following. I have graded RTDL against each honestly.

| # | Champion-maker | RTDL today | Why |
|---|---|---|---|
| 1 | **The problem is one the community already knows it has** | **Weak** | The paper must first convince the reader that cross-callback protocol incoherence is a real problem. Reviewers champion papers that solve something they have personally been bitten by. |
| 2 | **The mechanism is obviously right once seen** | **Strong** | "The complete callback protocol is the compilation unit, not the kernel" is a clean, memorable, reusable idea. The protocol-IDL framing lands. This is your best asset and it is already done. |
| 3 | **The evidence survives the reviewer's own attack** | **Medium** | The ablations are real and I verified them. But five injected defects on two author-designed tasks reads as "they tested their own toy," and the obvious counter — "a real developer's own oracle would catch these" — needs a stronger answer than it currently has. |
| 4 | **Generality demonstrated, not asserted** | **Zero** | Two closed public protocol families. Arbitrary Callback IR is not GPU-executable. Zero prospective exams. This is the largest single blocker. |
| 5 | **Somebody outside used it** | **Zero** | Zero third-party authors, zero usability studies. |
| 6 | **The result changes what the reader will do next** | **Conditional** | Only if 1 and 4 land. Today a reader admires the idea and goes home. |

**You have #2 outright and #3 partially. Strong accept needs #1 and #4 as well.** Everything below is about buying those two.

---

## 2. The gap list, ranked by champion-impact per unit of cost

### A. Real protocol defects in real third-party RT-repurposing code — **highest impact, lowest cost, no GPU required**

**This is the single highest-value thing you are not doing, and it is the one I would drop other work for.**

Right now the paper says: *we injected five defects and our checker caught them.* A reviewer's honest reaction is *"you injected defects into your own code; of course."* The paper you want says: *we examined N published, open-source RT-repurposing artifacts; in all of them, none of the five protocol properties is enforced anywhere; in K of them we identified a concrete site where a violation would be accepted silently; here is a compiler that makes that class impossible.*

That single change converts the problem from **asserted** to **observed**, which is champion-maker #1, and it simultaneously answers champion-maker #3, because a defect found in someone else's released code cannot be dismissed as a toy.

You are unusually well positioned for this. You have a 186-row exposure registry, you have re-implemented nine of these applications, and the 2026 literature review catalogues 35 novel RT solutions across 32 problems. You know these codebases better than almost anyone alive.

**Design.**
1. Select 8–12 published, open-source OptiX/RT-repurposing artifacts. Freeze the selection rule *before* looking at the code — e.g. "every artifact in the 2026 survey with a public repository and an OptiX backend" — so it is a census, not a hunt.
2. For each, extract the callback protocol by hand: which programs exist, which payload/attribute slots are used, what each program writes and reads, what the host does with device status and capacity.
3. Check each of the five properties: effect closure, payload/attribute meaning and ownership, physical binding consistency, status-before-consume, checked-program-to-executable identity.
4. Report three tiers, and keep them separate:
   - **enforced** — the artifact checks the property;
   - **unchecked but apparently correct** — nothing enforces it, but the code happens to agree;
   - **violated** — a concrete site where the protocol disagrees.
5. Even a result of "**0 of 12 enforce any of the five properties**" is a strong result. "Nobody checks this" is the residual claim, stated empirically instead of by construction.
6. **Responsible disclosure**: notify the authors of anything you classify as violated, offer a patch, give them time, and consider anonymizing artifacts in the paper. Do this properly — a paper that publicly accuses colleagues without notice will be punished for it regardless of correctness.

**Cost:** 1–2 careful days per artifact for protocol extraction. 8–12 artifacts ≈ 2–3 weeks with two people. **A reduced 3–4 artifact version is feasible in the next 12 days** and is still a large upgrade on five synthetic mutations.

**Risk:** you find that everyone already gets it right. That is a real possible outcome and it would substantially weaken the paper — which is exactly why it is worth running. If the defect class does not exist in the wild, you need to know before a reviewer tells you.

### B. A third protocol family, instantiated post-freeze, without a core change — **high impact, medium cost**

This is my standing Goal5804 P1-1 and it is still open. The paper claims a *protocol-IDL and admission layer*. An IDL whose only instantiable interfaces are two that ship hardcoded is not yet an IDL. A reviewer will say: *"you have two library entry points and a checker for their fixed declarations; where is the compilation unit?"*

Adding a third **protocol** family inside an existing **geometry** family — different hit policy, multiplicity, decode or continuation shape over `custom_aabb` or `builtin_triangle` — with the core frozen beforehand, converts "two hardcoded families" into "the admission model instantiates new protocols, and we added one after freezing." If it fails, you have learned something decisive about your own architecture that you need to know before writing the contribution sentence.

**Cost:** days if the architecture permits it; a redesign if it does not. **Answer this question first, this week, regardless of which submission you target**, because the contribution sentence depends on the answer.

### C. Generic Callback-IR → GPU authoring — **highest impact, highest cost**

This is the real product gap and the real reason #4 is zero. Until a user can write a new restricted-Python callback protocol and have it reach the GPU without a core edit, RTDL is an admission model with two instantiations rather than a compiler.

**This is the difference between "interesting bounded contribution" and "a compiler people will use."** It is also weeks-to-months of work and cannot be faked.

**Cost:** the honest estimate is 1–3 months, and it should be scoped by first answering B.

### D. One genuinely external developer — **high impact on your second standing concern, calendar-bound**

Not an agent proxy. A person outside the project, using only the shipped wheel and public documentation, implementing a task specified by someone who is not you. Recruiting plus an institutional determination plus their availability is a multi-week calendar problem regardless of how much money you throw at it.

The agent proxy you designed is a reasonable *documentation-sufficiency* probe and should be reported categorically — did the docs suffice, which private-API attempts occurred, which manual OptiX obligations surfaced — with no timings and no human inference. It does not substitute for D.

**Cost:** 3–6 weeks of calendar, mostly waiting.

### E. A checker-off ablation isolating the true checker cost — **medium impact, low cost**

Today you can say what the *whole lifecycle* costs (+163–223 ms setup, ~0 steady) but not what the *checking* costs, and you correctly refuse to claim otherwise. A reviewer will ask "so how expensive is the actual contribution?" and "we cannot separate it" is a weak answer for a paper whose contribution is the checking.

Run an arm with the identical frozen artifact where admission is bypassed at load, and report the difference. Note the caution from my Goal5799 P1-1: if every executable byte is identical, the *steady* comparison is a tautology and must be reported as a structural argument, not a measurement. The informative number is the **setup** delta: of the +163–223 ms, how much is admission and how much is everything else.

**Cost:** 1–3 days. **Do this one for the September submission if you do nothing else from this list.**

### F. More tasks, a second GPU, an OWL timing arm — **low impact per unit cost**

Nobody strong-accepts a paper because n went from 2 to 4. Reviewers ask for these in reviews, and you should be ready to add them in a revision, but they do not create champions. **Do not spend the next twelve days here.**

---

## 3. Plan A — the twelve days you actually have (2026-08-30 → 2026-09-10)

Assumes the writing week stays protected and the engineering hard stop holds.

| Window | Item | Why |
|---|---|---|
| **Aug 30 (1 day)** | **B, answer only**: can a third protocol family be instantiated inside an existing geometry family without a core change? Yes/no, recorded. | The contribution sentence depends on it. If yes, it is the cheapest large upgrade available. If no, the framing must narrow *before* the manuscript is written. |
| **Aug 30–31 (2 days)** | **E**: checker-off setup ablation. One number: of the +163–223 ms, how much is admission. | Answers the question every reviewer will ask about your own contribution's cost. Cheap. |
| **Aug 30 – Sep 3 (parallel, 2 people)** | **A, reduced**: 3–4 published artifacts, census-selected, five properties each, three-tier classification, disclosure started. | The largest single upgrade to the paper's persuasiveness available in the window. Converts the problem from asserted to observed. |
| **Aug 31 – Sep 6** | Manuscript. Absolute times in milliseconds (my Goal5817 P1-2). Direct prepare-phase explanation (P1-1). Per-arm phase composition. Bootstrap specification in methods. Abstract carries the two-family limit and the three zeros. | These are the two things standing between the current draft and "submission-ready," and they cost pages you already have — 7 of 11 used. |
| **Sep 7–9** | Double-blind manuscript scan + artifact scan, two separately gated passes. Final claim-source matrix. | A blinding violation is a desk reject. Do not leave it in "buffer." |
| **Sep 10** | Owner decision. | |

**What Plan A buys you:** a paper that says *this defect class exists in released code, nobody enforces these properties, here is a compilation unit that makes them checkable, here is exactly what it costs in milliseconds, and here is precisely how far it generalizes — which is two protocol families, and we say so.*

That is a good paper. Expect **borderline-to-accept**, with a real chance of rejection on "two tasks, no external users, no general authoring path." It is not a strong accept and you should not write it as though it were.

---

## 4. Plan B — the strong-accept program (≈3–6 months)

Target the next appropriate deadline rather than this one. Verify the specific dates yourself; treat the sequencing, not the calendar, as the content here.

**Month 1 — close the generality gap (C, gated by B).**
Generic Callback-IR → GPU authoring. A user writes a new restricted-Python protocol; the admission model checks it; it reaches the GPU; no core edit. Milestone: **three new protocol families instantiated by someone who did not build the compiler**, at least one outside the two current geometry families if the geometry work is tractable.

**Month 1–2 — the in-the-wild defect study at full scale (A).**
8–12 artifacts, census selection frozen in advance, full three-tier classification, disclosure completed, author responses recorded. Milestone: a table a reviewer cannot dismiss.

**Month 2–3 — external authorship (D).**
Institutional determination first. Two to three external developers, each implementing a task specified by a fourth party, using only shipped materials. Record every failure, documentation gap, private-API attempt and manual OptiX obligation, and count them against RTDL. Milestone: **a non-zero third-party author count**, with the friction reported honestly.

**Month 3 — the prospective exam you have been unable to run (your Goal5803 design).**
Now it is meaningful, because with C done a new task is not restricted to two hardcoded families. Use the design you already froze — it is good — with the reviewer-draw branch over a hand-enumerated, fully-bound table rather than an automated provider snapshot. Milestone: **one prospective exam completed with the outcome accepted unconditionally**, including failure.

**Month 3–4 — performance at the scale reviewers expect.**
Four to six tasks, two GPU generations, the OWL timing arm, the checker-off ablation, absolute times throughout. Milestone: the cost story is complete rather than bounded.

**Month 4–5 — write.**

**What Plan B buys you:** a paper that says *here is a defect class that exists in released work; here is a compiler abstraction that eliminates it; here is a general authoring path; here are people outside our group using it; here is a prospective test we could have failed and did not; and here is what it costs.* That is a champion's paper. It hits #1, #3, #4, #5 and #6, and you already have #2.

---

## 5. Why these items and not others

**Why the in-the-wild study is worth more than another benchmark.** Compiler-safety papers live or die on whether the reader believes the defect class matters. Every extra benchmark configuration answers a question nobody asked; one real bug in a published artifact answers the only question that matters. This is why bug-finding papers with modest techniques and real findings beat elegant techniques with synthetic evaluations, consistently, at every systems venue.

**Why generality outranks performance.** You already have the performance answer and it is fine: one-time ~0.2 s, no per-execution cost. Making it 0.1 s changes nobody's vote. Making the abstraction usable for a protocol you did not write changes the paper's category.

**Why an external user outranks a third task.** Your second standing concern — *"用户一用,一编程,发现特别难用"* — is not answerable by you, ever, at any level of effort, because you are the authors. Only an outsider's hands answer it. One outsider is worth more than ten more author-built tasks.

**Why the checker-off ablation is cheap and necessary.** Your contribution is the checking. You currently cannot say what the checking costs. That is an awkward sentence in a rebuttal and a trivial experiment to run.

---

## 6. The decision I would make, and why

**I would submit on September 10, and I would not expect a strong accept.**

Reasons:

1. **The reviews are worth more than the slot.** You will get three or four expert adversarial reviews from exactly the community you are targeting, for free. That is the input you have been paying me to approximate, from people who have built these systems. Whatever the outcome, those reviews are the best possible input to Plan B.
2. **CGO has a rebuttal and a second round.** A borderline submission is not wasted.
3. **The paper is honest.** After eight cycles I can say that nothing in it overstates. An honest paper that gets rejected costs you a submission slot; a dishonest one that gets accepted costs you everything you have spent four weeks building. You are not at risk of the second and you should not act as though a rejection were catastrophic.
4. **Plan B is better with the reviews in hand than without them.**

The one condition: **submit the bounded paper, not a padded one.** If the twelve days produce the in-the-wild study, include it. If they do not, submit without it and say the evaluation is bounded. Do not pad, do not stretch, do not manufacture.

If you would rather not spend the slot, the alternative is to withdraw from September 10 and run Plan B against the next deadline. That is also a defensible choice. It is not the one I would make, because the reviews are worth more than the slot.

---

## 7. The seven ways "不惜一切代价" destroys this project in the next twelve days

This is the most important section. Every item below is something your own record shows you are capable of, under pressure, in good faith.

1. **Boundary shopping.** You did it once, in Goal5807, and disclosed it. Under deadline pressure the temptation returns as "one more lifecycle decomposition." Any new measurement boundary defined after seeing a result is not a test. **Rule: no new regime, prefix, or derived quantity may be defined between now and submission.**

2. **Asymmetric baselines.** You did it once, in Goal5798, and it cost you your only favourable result. Every optimization you apply to RTDL in the next twelve days must be matched by an equivalent audit of the other arms — or you must apply none. **Rule: no arm-specific optimization before submission.**

3. **Manufacturing a generalization exam.** A "new application" chosen because it fits one of the two families is not a new application. A re-skin of an existing app is not a new application. **Rule: if the prospective exam cannot be run properly, the count stays zero and the paper says zero.**

4. **Promoting the agent proxy.** It is a documentation-sufficiency probe. The moment it is reported with timings or failure counts, a reader converts it into a usability claim. **Rule: categorical reporting only; `third_party_human_author_count` stays 0.**

5. **Padding to eleven pages.** You are at 7 of 11. Fill the space with absolute times, the Direct-prepare explanation, the per-mechanism OWL table, the 19-leaf table, and the in-the-wild study if it exists. Do not fill it with restated governance, artifact volume, or process narrative. **Reviewers punish volume that is not evidence** — and your CFR to me said exactly this, correctly.

6. **Resurrecting withdrawn results.** The Goal5798 v11 prepared win and the Goal5807 boundary passes are both permanently withdrawn. Under pressure they will look available. **Rule: an explicit scan of the manuscript, figures and artifact for both, as a blocking pre-submission gate.**

7. **Skipping the blinding scan because there is no time.** A double-blind violation is a desk reject, and it would waste every one of the previous six items. **Rule: two separately gated passes — artifact and manuscript — with a named owner, before anything is uploaded.**

---

## 8. What I would tell you if you asked me for one sentence

**Your idea is good enough for a strong accept; your evidence is not, and the missing evidence is generality and outside hands — neither of which money or effort can buy in twelve days, and both of which are straightforwardly buyable in three months.**

Submit the honest bounded paper in September, use the reviews, and build the strong-accept version for the next deadline. The thing that makes that plan viable is the thing you have actually accomplished over these four weeks, which is not any single result: it is that this project's record can be checked by a hostile stranger and survives. Very few submissions can say that. Do not spend it in the last twelve days.

---

*Advisory only. Authorizes no claim, no experiment, no execution and no submission. Prospective new-application exams: 0. Third-party human authors: 0. Usability studies: 0.*
