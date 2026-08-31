# Goal5815 CGO manuscript claim spine

This document supersedes the scientific claims in the 2026-08-16 outline. It is a drafting source, not the submitted paper.

## Working title

**Whole-Protocol Admission for Repurposed Ray-Tracing Programs**

The title deliberately avoids “general-purpose,” “safe Python,” “zero overhead,” and “automatic mapping.”

## One-sentence contribution

RTDL makes a bounded repurposed OptiX callback protocol—not an individual shader—the unit of admission, checking cross-role effects, payload/attribute meaning, physical bindings, status-before-consume, and executable identity before launching either of two closed public protocol families.

## Abstract claim block

Ray-tracing APIs validate program and platform legality but leave application meaning distributed across host composition, multiple device callbacks, payload and attribute conventions, continuation code, and the executable that is ultimately launched. We present RTDL, a bounded whole-protocol admission model for repurposed OptiX computations. RTDL checks cross-role effects, semantic ABI ownership, physical bindings, status-before-consume, and executable identity, then exposes a typed lifecycle for two closed public protocol families. On two matched non-rendering tasks, all 19 populated contract leaves are decision-bearing; five protocol-invalid programs reach execution through PyOptiX and NVIDIA OWL, while RTDL rejects their corresponding mutations before launch. Across nine project-authored applications, thirteen representative lanes execute exactly through the base callback path and six application-neutral M1–M6 composition batches; one project-selected SQL bag-equijoin reuses an existing public family without a core change, but prospective unbiased new-application exams and third-party authors both remain zero. On an RTX 4000 Ada, steady E2E is within 5% of matched PyOptiX on both measured tasks, while preparation and post-import deployment cold are 47–88% slower. RTDL does not discover ray-tracing mappings and does not claim arbitrary Callback IR execution, usability superiority, or current-source parity with direct CUDA/OptiX.

## Contributions list

1. A whole-protocol admission representation for a bounded class of non-rendering OptiX computations, covering cross-role effects, payload/attribute semantics and ownership, physical binding, status/continuation ordering, and checked-executable identity.
2. An executable implementation with two closed public GPU protocol families and a typed materialize–prepare–execute–close lifecycle, plus the base callback path and six M1–M6 composition batches spanning nine project-authored applications and thirteen representative lanes.
3. Mechanism evidence showing 19/19 populated semantic leaves individually affect admission and five protocol-invalid PyOptiX/OWL executions reach launch while RTDL rejects the corresponding mutations beforehand; the OWL residual is reported as 3 full + 1 partial + 1 binding-support.
4. A bounded application-reuse result: one project-selected SQL bag-equijoin reuses an existing family without a core change, beside a preserved failed BED transfer; neither is represented as prospective generalization.
5. A lifecycle-separated performance result: current checked steady E2E is within 5% of matched PyOptiX on two tasks, while preparation and post-import deployment cold remain 47–88% slower.

## Evaluation questions

1. Do the declared obligations control admission, or are any populated leaves decorative?
2. Do PyOptiX and OWL already prevent the same whole-protocol faults?
3. What application semantics and public protocol families are actually executable?
4. Can an application outside the original relation fixture reuse a frozen public family without a core change, and what failed transfer bounds that result?
5. What is the lifecycle-separated cost relative to matched idiomatic PyOptiX, and what Direct CUDA/OptiX evidence is from a distinct predecessor identity?

## Required main-text tables

1. Baseline responsibility table: Direct/PyOptiX/OWL/RTDL, with OWL composition credited and protocol residual separated.
2. Mechanism table: five rows with reached-launch, wrong-output/partial consequence, valid control, RTDL pre-launch decision, and claim strength.
3. Capability table: 9 authored applications / 13 lanes / base path + 6 composition batches / 2 public families, plus expression limits.
4. Reuse-boundary table: SQL success, BED failure, prospective exam count 0, third-party author count 0.
5. Performance table: Goal5805 current RTDL/PyOptiX six rows; separate Goal5802 historical Direct context with target/source warning.

## Mandatory limitation language

RTDL exposes exactly two closed public GPU protocol families and does not publicly execute arbitrary verified Callback IR. The application cohort is project-authored. The SQL reuse case was project-selected after a failed transfer; it is not blind, held-out, prospective, unbiased, or third-party evidence. Prospective unbiased new-application exams, third-party authors, and human usability studies are all zero. The current performance result contains no Direct CUDA/OptiX arm; older Direct data use a predecessor identity and different GPU. These limits constrain the generality, usability, and performance claims.

## Forbidden sentences

- RTDL supports arbitrary new repurposed RT applications.
- RTDL is easier, shorter, or more productive than PyOptiX, OWL, or CUDA/OptiX.
- RTDL adds no performance overhead.
- RTDL is currently as fast as direct CUDA/OptiX.
- OWL cannot construct or manage OptiX pipelines, SBTs, or acceleration structures.
- Five independent novel mechanisms are absent from OWL.
- The SQL witness is a held-out or prospective generalization exam.
- The nine-app cohort proves public-language generality.

## Related-work sentence

PyOptiX exposes OptiX mechanisms and OWL productively owns host composition; Slang, Dr.Jit, and CrossRT address target capability, traced rendering optimization, and algorithm-to-backend translation, respectively. Their cited abstractions do not establish the evaluated compiler-owned non-graphics callback-protocol contract; equivalent protection would require adding corresponding cross-role admission obligations.

## Submission decision rule

Submit only the bounded compiler/safety story. If the paper cannot keep the two-family limit, zero prospective exams, zero third-party authors, mixed cold/prepare result, and missing current Direct arm visible, the correct action is to narrow the paper rather than hide those facts.
