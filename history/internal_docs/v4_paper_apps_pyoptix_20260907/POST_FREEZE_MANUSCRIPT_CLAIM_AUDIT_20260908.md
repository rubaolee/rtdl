# Post-freeze manuscript claim audit for the application/PyOptiX evidence

Date: 2026-09-08 America/New_York.

## Decision

`CURRENT_R2_APPLICATION_SECTION_IS_STALE__REPLACE_BEFORE_ANY_FINAL_BYTE_REVIEW`

This audit compares the current untracked group-review R2 manuscript snapshot
against the frozen first-batch authority at source commit
`c5c8be48b743aa001e9c16c3344cc97c200600d1`. It does not edit or accept the
lead-owned manuscript. The proposed replacement text is
`MANUSCRIPT_APPLICATION_RESULTS_REPLACEMENT.tex` in this directory.

## Blocking inconsistencies

1. `paper/group_review_20260907_r2/main.tex:83` says the extension is in
   progress and `main.tex:84` says there are zero validated comparisons. The
   frozen state is now 192/192 formal workers passing, zero retries/discards,
   and an independent 192-file recount match for three of nine applications.
2. `paper/group_review_20260907_r2/application_extension.tex:1` labels the
   section pending; lines 4--22 repeat a pre-dry-run snapshot and zero-result
   caption. Those statements are historical, not current manuscript facts.
3. `application_extension.tex:60--70` preserves a source-level Triangle
   entry-selection inconsistency from an earlier source. The final frozen
   transaction executes the corrected registered Triangle route, returns the
   exact count 2,224,385, and passes all 48 Triangle workers. The old audit can
   remain in review history but cannot describe the final measured source.
4. `application_extension.tex:98--119` describes the protocol in future tense.
   The frozen transaction has already executed that protocol. Final prose must
   state the actual repetition exception: Particle prepared retained 32 calls
   per worker, while Triangle and each LibRTS unit retained four.
5. The current application section contains no final A/C values. All twelve
   endpoint ratios are adverse, from 1.079542x to 75.533295x. Omitting this
   table while retaining favorable synthetic A/D and A/C observations would
   materially misrepresent the evaluation.
6. A second post-freeze source audit found that the registered `complete` timer
   begins after `_load_input`. That loader performs material application work:
   Triangle degree orientation/filtering/deduplication/CSR construction and
   LibRTS WKT-to-query conversion are excluded. The endpoint cannot be called
   raw-domain end-to-end or said to fulfill the original all-encoding objective.
7. `first_result` begins after `_prepare_case`; it is the first checked execute
   on a prepared owner, not cold start or first result from a fresh environment.
8. Particle outputs match, but its physical device algorithms are not
   operation-identical. V4 enumerates and canonicalizes candidates through
   any-hit plus `optixIgnoreIntersection`; PyOptiX sets
   `OPTIX_RAY_FLAG_DISABLE_ANYHIT` and uses native closest-hit. This difference
   must be disclosed and prevents allocating the 37.93x prepared ratio to DSL
   checks or host/runtime overhead.
9. Triangle's `execute` routes are not lifecycle-identical. Both rebuild
   per-segment geometry/GAS, but V4 also builds and destroys its composed
   module/program groups/pipeline/SBT per segment while PyOptiX retains those objects from
   `_prepare_case`. The PyOptiX device program is handwritten CUDA/OptiX, not
   Numba. Therefore neither `first_result` nor `prepared` is a controlled
   measurement of Numba callback code-generation overhead.

## Required manuscript changes

1. Replace the current `application_extension.tex` body with the proposed
   result section or an equally complete version derived from the same formal
   summary. Keep the nine-application denominator and explicitly identify the
   six unexecuted applications.
2. Replace the internal-review notice at `main.tex:83--86`. It may say the
   first batch is complete and adverse, but must not say the nine-application
   campaign is complete.
3. Balance the abstract's favorable synthetic prepared observation at
   `main.tex:55--59` with the application result. A bounded accurate sentence
   is: "A separate frozen comparison completed three of nine application
   mappings; V4 was slower than competent public PyOptiX at all twelve measured
   endpoints, with prepared ratios from 1.379x to 39.083x."
4. Preserve the distinction among generated callbacks, partner composition,
   and closed specializations. Do not describe LibRTS count as arbitrary
   callback lowering or Triangle partner reduction as compiler-generated RTDL
   callback work.
5. State what each app author still supplies and what RTDL generates, checks,
   and reuses. The responsibility paragraph in the replacement file satisfies
   this requirement for the three executed applications.
6. Report the same registered derived-input, same-complete-output endpoint cost.
   Identify excluded application preprocessing and the post-prepare meaning of
   `first_result`. Do not call the total V4/PyOptiX ratio intrinsic language
   overhead, compiler overhead, or validation overhead; no causal ablation
   supports that allocation.
7. Keep Goal5848's two synthetic tasks separate. Their near-Direct and
   favorable prepared A/C observations do not substitute for application
   evidence or prove the general Numba-leaf route competitive.
8. Disclose that PyOptiX PTX was compiled before worker zero while ordinary V4
   Particle and Triangle compilation remains in `complete` preparation. Also
   disclose Triangle's per-segment lifecycle difference and handwritten
   CUDA/OptiX PyOptiX device program.
9. Do not call `first_result` pure launch: only `_prepare_case` is excluded, and
   Triangle retains material per-segment setup inside `execute`. Also disclose
   that timed execute includes adapter oracle/status checks, digest work, and
   compact evidence projection rather than isolated native-runtime latency.
10. State that Particle uses a project standard-library callback. Do not claim
    easier authoring: this packet contains a responsibility comparison but no
    independent authoring study.

## Verified numerical basis

- Final formal summary SHA-256:
  `67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf`.
- Independent recount SHA-256:
  `667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64`.
- Compact archive SHA-256:
  `2d7dc4413639e46994ca74251d230b74d5e9d775a23b457336cb00f9df80f4ff`.
- Machine: NVIDIA RTX A4500, compute capability 8.6, driver 550.127.05,
  OptiX SDK 8.0.0, PyOptiX 9.1.0.
- Formal population: 192 unique fresh-process workers, 96 paired
  registrations, 12 evaluated unit/endpoints, zero retry/discard.
- Coverage: three of nine applications, four operation units. The remaining
  six rows are unexecuted, not failures and not omitted successes.
- Every displayed table value was independently reconstructed from the 96
  formal registrations and matched the controller's 12 evaluations.

## Claim ceiling

The first-batch evidence is ready to share internally with the above caveats.
It is not a positive performance result. Public/manuscript speedup,
near-PyOptiX, nine-application completion, usability, upload, submission, and
final-byte acceptance remain unauthorized. Any final manuscript must undergo a
new exact-byte review after these results are integrated.
