# Full RayJoin Repetition Feasibility Report

Date: 2026-04-02

## Purpose

This report evaluates the feasibility of the next major project goal:

- repeat the RayJoin paper experiment set on `192.168.1.20`
- use both controlled RTDL backends:
  - Embree
  - OptiX
- keep run times bounded and technically honest

This is a planning and risk report, not a claim that full reproduction is
already finished.

## Current position

The project now has a much stronger foundation than it had before the Linux
GPU and native-oracle work.

### What is already solid

- native C/C++ oracle exists and replaced the old Python-only simulator core
- small correctness checks established:
  - Python oracle == native oracle == Embree
- Embree backend has real exact-source Linux evidence for multiple RayJoin
  families
- OptiX backend has real GPU-host execution on `192.168.1.20`
- OptiX bounded County/Zipcode ladder is now parity-clean after Goal 46

### Strongest current published evidence

Embree:

- `County ⊲⊳ Zipcode`
- `BlockGroup ⊲⊳ WaterBodies`
- bounded `LKAU ⊲⊳ PKAU`
- large-scale Embree-only feasibility accepted through:
  - `top4_tx_ca_ny_pa`

OptiX:

- authored correctness ladder from Goal 43
- bounded synthetic performance from Goal 44
- first real exact-source family:
  - `County ⊲⊳ Zipcode`
- bounded parity-clean ladder after Goal 46:
  - `1x4`
  - `1x5`
  - `1x6`
  - `1x8`
  - `1x10`
  - `1x12`

## What “full RayJoin repetition” means here

For this project, “full repetition” should be defined carefully.

It cannot honestly mean:

- identical hardware to the RayJoin paper
- identical RT-core environment
- immediate full paper-scale nationwide/continent-scale execution for every
  family on this single workstation

It can honestly mean:

- reproduce the RayJoin experiment structure on this Linux host
- cover the same workload families as far as the host and public data allow
- run both Embree and OptiX backends where the backend is mature enough
- regenerate the corresponding tables/figures with explicit fidelity labels:
  - full exact-source
  - bounded exact-source
  - analogue
  - missing

That is the correct standard for v0.1 on the current infrastructure.

## Feasibility assessment

## Overall feasibility

- finishing a serious **Embree + OptiX RayJoin repetition package** on this host:
  - **feasible**
- finishing a literal “same hardware class, same RT-core story, same scale for
  every family” repetition:
  - **not feasible on this host**

## Embree feasibility

Embree is the stronger backend right now.

Why:

- more dataset families already exercised
- more exact-source evidence already published
- larger Linux runs already completed
- current correctness state is stronger and more mature

Embree is already close to a full bounded reproduction package. The remaining
work is mostly:

- fill remaining family holes
- consolidate final tables/figures
- refresh reports under one final matrix

Assessment:

- Embree-only final repetition package:
  - **high feasibility**

## OptiX feasibility

OptiX is now real, but less mature than Embree.

Why:

- real GPU execution exists
- first real exact-source family now has bounded parity closure
- but only one real-data family has been closed at that level
- current Goal 46 correctness repair uses:
  - GPU candidate generation
  - exact host-side refine

That means OptiX is now trustworthy on the tested bounded ladder, but the
backend still needs broader real-data coverage before it can stand beside
Embree as a full repetition backend.

Assessment:

- bounded multi-family OptiX repetition package:
  - **moderate feasibility**
- full paper-style OptiX repetition across all families on this host:
  - **possible but still risky**

## Host feasibility

Host:

- `192.168.1.20`
- CPU: multi-core workstation-class laptop CPU
- RAM: about `15 GiB`
- GPU: `NVIDIA GeForce GTX 1070`
- OptiX runtime: `9.0`
- no RT cores

Implication:

- good for:
  - bounded exact-source reproduction
  - medium-scale state/multi-state runs
  - GPU bring-up and bounded GPU validation
- not ideal for:
  - very large nationwide polygon-heavy joins on both backends at once
  - unconstrained paper-scale continent-wide reruns with long iterative debug
    cycles

So the host is good enough for a serious v0.1 repetition package, but not for
unbounded “run everything at original scale no matter how long it takes.”

## Remaining work to reach a full repetition package

The missing work is now mostly experiment and integration work, not a fresh DSL
or backend redesign.

## Embree-side remaining work

1. Close any remaining RayJoin family gaps not yet run end to end on Linux.
2. Decide the final accepted scale for each family on this host.
3. Consolidate final Embree artifact coverage:
   - Table 3
   - Table 4
   - Figure 13
   - Figure 14
   - Figure 15

## OptiX-side remaining work

1. Move beyond County/Zipcode to the next real family:
   - best candidate: `BlockGroup ⊲⊳ WaterBodies`
2. Establish bounded correctness and timing there against the native oracle.
3. Decide whether the current host-refine OptiX design remains acceptable for
   that family or requires more backend work.
4. Add one more representative family if time permits:
   - likely bounded `LKAU ⊲⊳ PKAU`

## Cross-backend consolidation

1. Produce one final matrix mapping every paper family to:
   - Embree status
   - OptiX status
   - fidelity label
2. Regenerate final reports and paper-style summary documents.
3. Make explicit where OptiX is:
   - fully bounded and parity-clean
   - bounded but still missing
   - not yet attempted

## Estimated goal count

Reasonable remaining goal count:

- **minimum:** `4`
- **more realistic:** `5-7`

Suggested shape:

1. OptiX `BlockGroup ⊲⊳ WaterBodies` correctness + bounded performance
2. OptiX next family or broader County/Zipcode scaling
3. remaining Embree family/matrix cleanup
4. cross-backend table/figure regeneration
5. final full repetition report

## Time estimate

## Best-case estimate

If no new major backend bug appears:

- about **4-6 focused working days**

This assumes:

- datasets stay accessible
- OptiX closes its next family without a new correctness crisis
- consolidation is mostly documentation/reporting work

## Realistic estimate

More realistic end-to-end estimate:

- about **1-2 weeks**

Reason:

- at least one more real OptiX family is still unproven
- final matrix/report work usually takes longer than expected
- review/consensus cycles add latency

## Worst-case estimate

If OptiX shows another real-data correctness gap on the next family:

- about **2-4 weeks**

because the schedule becomes dominated by:

- diagnosis
- remote reruns
- review loops
- reclassification of what can be honestly called “full”

## Main risks

## Technical risks

1. **OptiX correctness on the next real family**
   - Goal 46 fixed County/Zipcode, but only on one family and bounded ladder.
   - Another family may expose a different candidate/refine problem.

2. **Performance collapse from host-side OptiX refine**
   - Goal 46 restored correctness by using exact host refine.
   - That may remain acceptable for bounded correctness validation but become
     unattractive for larger runs.

3. **Dataset pipeline edge cases**
   - new families can still expose:
     - conversion issues
     - invalid geometry
     - service availability drift
     - region-specific topology edge cases

4. **Host capacity**
   - memory/runtime could become the limiting factor before full-family runs are
     complete.

## Process risks

1. **Review latency**
   - Claude or Gemini quota/CLI behavior can slow closure.

2. **Overclaim pressure**
   - the biggest non-technical risk is claiming “full repetition” before all
     family statuses are explicitly classified.

## Publication-style risk

The final package will be strongest if it is framed as:

- a careful **RTDL multi-backend repetition package on current hardware**

and not as:

- a claim that a GTX 1070 OptiX run is equivalent to the RayJoin paper’s RT-core
  environment

That wording discipline matters.

## Token consumption estimate

This project uses heavy AI review/audit loops, so token cost is a real planning
input.

## Per-goal rough token estimate

For one nontrivial remaining goal:

- Codex local work + validation + write-up:
  - about `40k-120k` tokens
- one Gemini serious review round:
  - about `10k-40k` tokens
- one Claude serious review round:
  - about `10k-40k` tokens
- cross-review / final consensus write-up:
  - about `10k-30k` tokens

Typical total per serious goal:

- about **`70k-230k` tokens**

## Full remaining-program token estimate

For the estimated `4-7` remaining goals:

- **low estimate:** about `300k-500k` tokens
- **realistic estimate:** about `500k-1.2M` tokens
- **high estimate:** about `1.5M+` tokens if OptiX diagnostics reopen

## How to keep token cost under control

1. Keep each goal narrow and publishable.
2. Use Gemini for fast pre-review, Claude for final review where available.
3. Avoid re-auditing the whole repo unless a major trust break appears.
4. Reuse frozen datasets/slices and existing harnesses instead of creating new
   experiment frameworks per round.
5. Prefer exact-row diff tools and direct reproduction scripts over long
   free-form debugging discussion.

## Recommendation

The project is now in a position where a full bounded RayJoin-style repetition
package on this Linux host using both Embree and OptiX is **feasible**.

The right expectation is:

- not a literal same-hardware replay of the RayJoin paper
- but a serious, well-labeled, multi-backend RTDL repetition package

Recommended commitment level:

- proceed
- plan for **`5-7` remaining goals**
- budget roughly **`1-2 weeks`**
- budget roughly **`500k-1.2M` tokens** for a realistic full finish

## Final answer

### Feasibility

- **Embree final repetition package:** high
- **OptiX bounded real-data repetition package:** moderate to high
- **full cross-backend bounded repetition package on this host:** feasible

### Time

- best case: `4-6` working days
- realistic: `1-2 weeks`
- worst case with new OptiX issues: `2-4 weeks`

### Main risks

- new OptiX correctness gaps on the next family
- host-refine performance cost on GPU path
- host memory/runtime limits
- dataset/conversion edge cases
- review latency

### Token estimate

- realistic remaining budget: **`500k-1.2M` tokens**

That is a large but manageable final stretch, and the current foundation is now
strong enough that the remaining work is more execution risk than architectural
risk.
