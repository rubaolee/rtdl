# Claude Review: Goal1573 Derived Carry Alias Diagnostic

## Verdict

Positive diagnostic, not yet production-default. The mechanism is architecturally sound and the topology guard is correctly derived. Gains are real but modest and topology-dependent. Broader GPU/topology coverage is required before promotion.

## Correctness Risks

1. Topology guard relies on a precise layout invariant. Claude judged the guard `next_segment_count == 2 || (next_segment_count % 2) != 0` correct, and judged the blocked even `> 2` case necessary.
2. Merge/accounting counter is inflated on the alias path because the carry block increments transfer accounting even when no row payload `cuMemcpyDtoD` is issued.
3. Preconditions are implicit and should remain tightly guarded by derived descriptors plus batched compact level.
4. Carry count device-to-device copy is still necessary and correct.

## Performance Risks

Gains apply only to odd-carry levels and are modest at current scale. Evidence is from one RTX 4000 Ada pod only. More topology and hardware coverage is needed before production promotion.

## Required Next Tests

- Fix and re-audit carry accounting.
- Large-N and even-N sweeps.
- Small topology edge cases such as `3`, `5`, `7`.
- Additional GPU architectures before public speedup wording.

## Promotion Recommendation

Keep `RTDL_OPTIX_COLLECT_K_DERIVED_CARRY_ALIAS_DIAGNOSTIC=1` diagnostic until accounting is fixed and broader tests pass.
