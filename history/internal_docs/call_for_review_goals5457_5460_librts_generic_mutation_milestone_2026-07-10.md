# Consolidated Call For Review - Goals5457-5460 LibRTS Mutation Milestone

Please strictly review the complete mutation arc, not only the final matched
count sequence.

## Scope

```text
Goal5457: author/RTDL mutation contract audit
Goal5458: app-neutral MutableAabbIndex2D CPU contract and non-LibRTS consumer
Goal5459: Linux OptiX atomic snapshot-rebuild runtime gate
Goal5460: patched-author vs RTDL same-input mutation sequence
```

Primary documents:

```text
history/internal_docs/goal5457_librts_generic_mutation_contract_audit_2026-07-10.md
history/internal_docs/goal5458_generic_mutable_aabb_cpu_contract_2026-07-10.md
history/internal_docs/goal5459_generic_mutable_aabb_optix_snapshot_rebuild_2026-07-10.md
history/internal_docs/goal5460_librts_same_input_mutation_gate_2026-07-10.md
```

Implementation and evidence:

```text
src/rtdsl/mutable_aabb_index.py
src/rtdsl/__init__.py
tests/goal5457_librts_mutation_contract_audit_test.py
tests/goal5458_generic_mutable_aabb_index_contract_test.py
tests/goal5459_generic_mutable_aabb_optix_snapshot_rebuild_test.py
tests/goal5460_librts_same_input_mutation_gate_test.py
scripts/goal5459_generic_mutable_aabb_optix_gate.py
Paper-reproduction-apps/librts-paper/run_same_input_mutation_gate.py
Paper-reproduction-apps/librts-paper/author_patches/goal5460_author_mutation_probe.cu
Paper-reproduction-apps/librts-paper/author_patches/goal5460_fix_instance_update_temp_buffer.patch
history/internal_docs/goal5459_generic_mutable_aabb_optix_snapshot_rebuild_linux.json
Paper-reproduction-apps/librts-paper/results/librts_goal5460_same_input_mutation.json
```

## Decision-Critical Facts

```text
patched-author counts = [2,1,0,1,0]
RTDL OptiX counts      = [2,1,0,1,0]
automatic appended ID = 2 on both

author execution = native incremental GAS/IAS update
RTDL execution   = atomic prepared-snapshot rebuild
```

The unpatched author update path fails on the local OptiX runtime because
`updateInstanceAccel()` allocates `tempUpdateSizeInBytes` but passes
`tempSizeInBytes`. The disclosed one-line patch corrects that buffer-size
argument. Review whether this remains a legitimate compatibility patch and
whether all prose correctly calls the result patched-author evidence.

## Review Questions

1. Did Goal5457 correctly identify a missing generic system capability rather than an app-only gap?
2. Is stable-ID snapshot rebuild a coherent first public mutable AABB contract?
3. Does validation/new-prepare-before-swap provide sufficient failure atomicity?
4. Is the non-LibRTS dynamic-obstacle consumer behaviorally distinct and sufficient?
5. Does Goal5459 prove the public contract on real OptiX without making a performance claim?
6. Is the author update-buffer correction minimal, necessary, and fully disclosed?
7. Does the final gate align geometry, query, operation order, and ID lifecycle?
8. Is `[2,1,0,1,0]` discriminating enough for update/delete/insert/clear semantics?
9. Are native incremental implementation parity and mutation performance parity correctly unclaimed?
10. Is RTDL core free of LibRTS/paper/author identity?
11. Is Embree completely absent as required by owner scope?
12. Should native incremental/refit be a separate generic design goal rather than inferred from this milestone?

## Requested Verdict

```text
approve_goals5457_5460_librts_generic_mutation_semantics_milestone
```

Allowed conclusion: bounded same-input mutation result-count and ID-lifecycle
agreement is complete, with a generic RTDL snapshot-rebuild implementation.

Forbidden conclusion: RTDL reproduces the author's native incremental mutation
algorithm, mutation performance, paper figures, full paper, or Embree results.
