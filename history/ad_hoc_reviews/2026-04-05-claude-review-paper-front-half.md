---

## Review: RTDL Front-Half Sections

### 1. Verdict

**APPROVE-WITH-NOTES**

The paper is technically honest, the system motivation is clearly reasoned, and the "Why RTDL" section does solid work. However, the abstract has a jargon and self-assessment problem serious enough that a reviewer could bounce the paper on first read, and two structural decisions will raise flags from a program committee.

---

### 2. Findings

**Abstract (most urgent issues)**

- **Impenetrable performance claim.** The sentence "On the strongest accepted long exact-source `county_zipcode` positive-hit point-in-polygon surface..." is dense project-internal language. A reviewer reading the abstract cold does not know what "accepted," "long exact-source," or "positive-hit surface" mean. The claim is buried in its own hedges.
- **"Technically honest" is for reviewers to say, not authors.** The phrase "technically honest" appears twice in the abstract and is repeated in the body. It reads as defensive, flags that the paper is aware of a credibility problem, and invites skepticism rather than resolving it. Remove it; let the methodology speak.
- **"Overlay-seed evaluation" undefined at first use.** The abstract uses this term before §3.1 defines it. A reader can't assess the scope limitation without that definition.
- **"Accepted package surfaces" is unexplained jargon.** This phrase and "published prepared and repeated-call boundaries" have no anchor for a newcomer.

**Introduction**

- **Solid four-contribution list.** Each contribution is specific and bounded. Contribution 3 ("Cross-System Correctness Methodology") is slightly over-claimed as a "rigorous validation framework" — fine to call it a validation methodology.
- **The framing is slightly circular.** The paragraph structure is: RTDL reduces burden → we evaluate on RayJoin → RayJoin is the right target → paper does two things. The "central question" framing ("can such an abstraction remain technically honest") front-loads the defensiveness again.
- **"Payload conventions" used without definition.** Systems readers will follow; newcomers won't.

**What Ray Tracing Is and Why It Matters Beyond Graphics**

- **This is the best-written section in the front half.** The graphics-to-spatial bridge is clean and a non-expert can follow it.
- **Block-quote citation of RayJoin is unusual for IEEE conference style.** A full bibliographic block quote in the paper body (§3.1) looks like the paper is confirming authorship rather than citing a reference. Replace with a normal inline citation and a one-sentence description.
- **"RayJoin as the First Application Target" repeats material from the Introduction.** The paragraph beginning "RayJoin is the right first target for RTDL because it exercises the exact class of workloads..." is nearly verbatim from Introduction §2. This will cost words and feel like padding.

**Why RTDL and How It Works**

- **The five-bullet authored-surface list is the paper's clearest motivation passage.** Keep it.
- **The kernel listing is well-chosen and appropriately simple.**
- **"Goal 50 external comparison" in the Correctness Method subsection is an internal artifact reference** that will confuse any reviewer who is not the author. "After the Goal 50 external comparison exposed remaining boundary/topology mismatches" — this reads like a project log, not a paper. Rewrite to describe the event without the internal ticket number: "During development, a systematic comparison against PostGIS exposed remaining boundary/topology mismatches..."
- **"Lowered form" is used before "lowering" is defined.** First use of "lowers" is §4 headline; "lowered representation" appears earlier in §3.1. Ordering is fine but tighten the first definition.
- **Related Work placement is non-standard.** §4 (Related Work) sits between §3 (RT background) and §5 (Why RTDL). Standard IEEE structure puts Related Work at §2 or immediately after contributions. This placement interrupts the background-to-design flow and will draw a comment from reviewers.

---

### 3. Agreement and Disagreement

**What the paper gets right:**

- The scope discipline is genuinely unusual and admirable. Explicitly labeling cases as "deferred-unavailable" and "not claimed" is the right choice and will help with reproducibility reviewers.
- The three-tier correctness chain (native oracle → Embree/OptiX → PostGIS) is clearly described and correctly prioritized.
- The "Why a DSL Is Needed" framing correctly identifies that the problem is not traversal speed but setup/marshaling overhead — and the optimization list in Design Considerations confirms that.
- The kernel listing earns its place; it is concrete and the right level of abstraction for this section.

**Where the paper argues against itself:**

- The repeated use of "technically honest" signals a credibility anxiety that the paper's actual methodology does not warrant. The methodology is solid. Trust it without announcing it.
- The hedged abstract performance claim ("on the strongest accepted long exact-source... surface") is so qualified that it nearly cancels itself. If the claim is true, state it plainly and explain the scope in one parenthetical.

---

### 4. Recommended next step

**Rewrite the abstract in one pass** with these four targets:

1. Replace "accepted long exact-source `county_zipcode` positive-hit..." with a two-clause plain English statement: what workload, what result, and the one-sentence scope caveat.
2. Remove both uses of "technically honest."
3. Define "overlay-seed evaluation" with a parenthetical or replace with "overlay candidate generation."
4. Make the PostGIS performance claim legible — state a concrete direction (e.g., outperform on prepared-execution and repeated-call boundaries) without requiring the reader to decode internal vocabulary.

Then, as a second-priority fix: **move Related Work to §2**, excise the RayJoin block-quote in §3.1, replace the "Goal 50" reference in §4.3 with a description of the event, and cut the near-verbatim repetition between Introduction and §3.1. Those four edits together will clean up the most likely reviewer objections.
