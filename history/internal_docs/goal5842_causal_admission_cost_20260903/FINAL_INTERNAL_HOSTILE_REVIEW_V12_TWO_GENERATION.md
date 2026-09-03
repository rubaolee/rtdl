# Goal5842 V12 two-generation internal hostile review

Date: 2026-09-03

Review mode: internal hostile self-review only. External review and consensus
remain owner-deferred.

## Verdict

`ACCEPT_GOAL5842_AS_INTERNALLY_TECHNICALLY_COMPLETE__REJECT_PUBLIC_CLAIMS`

The exact V12 schedule completed on distinct Ada and Ampere GPUs, both
complete archives are hash-bound, both pod recounts reproduce byte for byte
from frozen Git blobs, and the frozen cross-generation gate accepts the two
generation and UUID identities. No required internal execution remains.

## P0 findings

None found within the preregistered technical scope.

## P1 findings

1. Public and manuscript performance claims remain blocked. The evidence has
   not received external review or consensus.
2. Both provider baselines are adverse. On Ampere, RTDL relation is 3.13x
   PyOptiX in steady execution and triangle is 155.21x; against Direct the
   values are 12.71x and 295.16x. Ada is also adverse. These rows must remain
   adjacent to the favorable causal diagnosis.
3. Triangle hidden work is not matched. RTDL copies an internal per-ray vector
   and performs host reduction, while Direct and PyOptiX return the public
   scalar. This is a fair current-public-implementation comparison, not an
   intrinsic language-overhead result.
4. V12 is not result-blind. V11 exposed registered timings before the
   independent validator's receipt-shape defect was corrected. V11 is
   preserved, excluded, and V12 is explicitly labeled post-result.

## P2 findings

1. The causal experiment isolates cold provider projection and generic-family
   admission. It does not isolate every later identity check or prove that any
   check may be removed.
2. Phase fractions combine separately summarized medians. They diagnose
   priorities but are not additive decompositions or registered estimands.
3. The two GPU generations use different drivers and OptiX APIs. Directional
   replication is valid; cross-machine raw-time ratios are not.
4. The baseline has two exact same-public-contract tasks, not arbitrary RT
   programs. Sphere appears only in the causal cohort because no honest matched
   three-provider baseline was frozen.
5. The archives bind exact source and binary identities but do not embed a
   complete hermetic Python package repository or CUDA/OptiX installation.
6. The frozen cross-generation builder records absolute recount paths. The
   generation authorities bind the portable file bytes and hashes; reviewers
   should not interpret those absolute paths as artifact identity.

## P3 findings

1. Both machines are rented cloud environments without exclusive physical-host
   attestation. The execution-authority idle-process gate detects visible
   foreign GPU processes but not every source of host noise.
2. A single workload scale and implementation revision cannot establish an
   asymptotic performance law.
3. The Ampere preflight required two compatibility repairs before worker zero.
   They are disclosed and did not change scientific inputs, but they reinforce
   the need for a reproducible environment recipe in the final artifact.

## Hostile attacks and responses

### "The safety checker makes RTDL slow"

Rejected as the dominant explanation. The registered admission delta is
27.7--38.0 ms on Ada and 42.8--55.7 ms on Ampere, while current setup gaps are
measured in seconds. On both generations, materialization plus native prepare
accounts descriptively for roughly 94%--97% of RTDL setup.

### "Disable checking and publish the faster route"

Rejected. Check-off is a private counterfactual, not a supported API. The
experiment gives no safety proof for removing later identity verification.

### "The baseline proves RTDL as a language is hundreds of times slower"

Rejected. It proves the current triangle lowering is hundreds of times slower
under this public scalar contract. The implementation unnecessarily crosses a
per-ray vector to the host and reduces there. That is actionable backend debt,
not a semantic lower bound.

### "Two generations make the timing hardware-independent"

Rejected. They establish replication of direction and phase diagnosis only.
Raw magnitudes differ and cannot be ratioed across machines.

### "The favorable conclusion hides adverse rows"

Rejected only because the reports and authorities retain every adverse ratio
and explicitly deny public performance authorization. Removing or separating
those rows would invalidate this review.

## Engineering consequence

The next goal must preserve public admission and target these measured costs:

1. reuse exact-identity compiled leaves, pipeline state, and prepared targets;
2. eliminate repeated Python/native input materialization where immutability
   and identity are proven;
3. route triangle per-ray values through generic device-resident checked U64
   reduction and return only the public scalar;
4. measure cold setup, warm reuse, first execution, and steady execution as
   separate contracts;
5. run any improved baseline under a new preregistration, never by rewriting
   V12.

These are nontrivial compiler/runtime contributions. More Goal5842 harness
polish would not address the observed bottleneck.

## Completion boundary

Goal5842 is internally complete because every preregistered two-generation
technical gate has passed and adverse findings are preserved. The later
external-review gate controls public/manuscript wording, not whether the
engineering transaction completed. Goal5841's unavailable external-human
authoring study remains a separate limitation and must not be silently
substituted with AI or project-author observations.
