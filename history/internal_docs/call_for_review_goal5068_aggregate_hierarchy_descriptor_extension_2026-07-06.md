# Call For Review: Goal5068 Aggregate Hierarchy Descriptor Extension

Date: 2026-07-06

Please review:

- `history/internal_docs/goal5068_aggregate_hierarchy_descriptor_extension_result_2026-07-06.md`
- `src/rtdsl/aggregate_hierarchy.py`
- `Paper-reproduction-apps/rt-barneshut-paper/aggregate_hierarchy_adapter.py`
- `tests/goal5068_aggregate_hierarchy_descriptor_extension_test.py`
- `tests/goal5067_rt_barneshut_aggregate_hierarchy_adapter_test.py`

## Requested Verdict Labels

Use one:

- `approve_goal5068_generic_descriptor_extension`
- `approve_with_required_amendments`
- `block_goal5068_descriptor_extension`

## Context

Goal5067 mapped RT-BarnesHut prepared arrays into `AggregateHierarchy3D` but left two fields as app-owned gaps:

- `source_leaf_node_index`
- `node_subtree_end_index`

Goal5068 promotes those fields as optional generic descriptor columns in the RTDL contract. It does not promote force-law semantics, comparator policy, author payload policy, or backend execution.

## Review Questions

1. Are `source_leaf_node_index` and `node_subtree_end_index` genuinely generic hierarchy traversal descriptors rather than RT-BarnesHut-specific app semantics?
2. Does the source-leaf descriptor validation correctly require one leaf-node index per point/source row?
3. Does the source-leaf descriptor validation correctly reject non-leaf references and leaves that do not contain the corresponding point?
4. Does the subtree-end descriptor validation correctly require an exclusive DFS range end for every node?
5. Does the subtree-end descriptor validation correctly reject child ranges outside the parent subtree range?
6. Did the RT-BarnesHut adapter correctly move these fields from app-owned gaps to `generic_descriptor_fields_promoted`?
7. Does the change avoid promoting `contract_source`, raw `tree`, raw `points`, raw `nodes`, comparator policy, or payload policy into RTDL core?
8. Does the change preserve the Goal5063/5066/5067 regression suite?
9. Does the result avoid backend, CUDA/native, paper-completion, and performance claims?
10. Is the proposed next step correct: define a backend-neutral execution contract for aggregate frontier reduce over `AggregateHierarchy3D`, still without implementing backend execution?

## Expected Review Output

Please include:

- verdict label;
- blocking findings, if any;
- required amendments, if any;
- non-blocking notes;
- answers to the 10 review questions.
